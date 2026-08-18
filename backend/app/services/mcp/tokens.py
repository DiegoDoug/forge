from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import generate_mcp_token, hash_mcp_token
from app.models.base import utcnow
from app.models.mcp_token import McpToken

# Write-throttling window for last_used_at (01_SPEC.md SS4.3) - avoids a DB
# write on every /mcp request under SQLite's single-writer model, for a field
# that only needs staleness-level precision.
_LAST_USED_THROTTLE_SECONDS = 5 * 60


@dataclass(frozen=True)
class McpTokenContext:
    """Returned by verify() on a successful check. Deliberately not the
    McpToken ORM row itself - matches the existing convention of never
    exposing ORM objects directly (07_CODING_STANDARDS.md SS1)."""

    token_id: str
    name: str
    scopes: frozenset[str]

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


def _parse_scopes(raw: str) -> frozenset[str]:
    return frozenset(s.strip() for s in raw.split(",") if s.strip())


def _serialize_scopes(scopes: list[str]) -> str:
    return ",".join(sorted(set(scopes)))


async def issue(session: AsyncSession, *, name: str, scopes: list[str]) -> tuple[McpToken, str]:
    """Creates a persistent token row and returns (row, raw_token). The raw
    value is never stored - the caller (POST /api/mcp/tokens) must return it
    to the requester now; it cannot be recovered after this call returns."""
    raw = generate_mcp_token()
    token = McpToken(name=name, token_hash=hash_mcp_token(raw), scopes=_serialize_scopes(scopes))
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token, raw


async def list_tokens(session: AsyncSession) -> list[McpToken]:
    result = await session.execute(select(McpToken).order_by(McpToken.created_at.desc()))
    return list(result.scalars().all())


async def revoke(session: AsyncSession, token_id: str) -> McpToken | None:
    """Sets revoked_at rather than hard-deleting the row, so revocation
    history survives for audit purposes (01_SPEC.md SS4.3.1). Returns None if
    no such token exists; idempotent if already revoked."""
    result = await session.execute(select(McpToken).where(McpToken.id == token_id))
    token = result.scalar_one_or_none()
    if token is None:
        return None
    if token.revoked_at is None:
        token.revoked_at = utcnow()
        session.add(token)
        await session.commit()
        await session.refresh(token)
    return token


async def verify(session: AsyncSession, raw_token: str) -> McpTokenContext | None:
    """Hashing is deterministic (HMAC keyed on the server's root key), so a
    valid token's hash can be looked up by exact equality against the
    indexed token_hash column - O(1), not a per-row scan. Revoked tokens
    never match (checked in the same query, so revocation is immediate with
    no caching window)."""
    candidate_hash = hash_mcp_token(raw_token)
    result = await session.execute(
        select(McpToken).where(McpToken.token_hash == candidate_hash, McpToken.revoked_at.is_(None))
    )
    token = result.scalar_one_or_none()
    if token is None:
        return None
    return McpTokenContext(token_id=token.id, name=token.name, scopes=_parse_scopes(token.scopes))


async def touch_last_used(session: AsyncSession, token_id: str) -> None:
    """Write-throttled - see module docstring. Silently no-ops if the token
    no longer exists (e.g. revoked-and-since-deleted in a future phase);
    verify() has already run by the time this is called, so a missing row
    here is not itself an auth failure."""
    result = await session.execute(select(McpToken).where(McpToken.id == token_id))
    token = result.scalar_one_or_none()
    if token is None:
        return
    now = utcnow()
    last_used = token.last_used_at
    if last_used is not None:
        # SQLite has no native datetime type - a freshly-created utcnow()
        # value is timezone-aware, but the same value reloaded from the DB
        # comes back naive (aiosqlite/sqlite3 strip tzinfo on read). Normalize
        # before subtracting so this doesn't crash on the second call ever
        # made against a given token.
        if last_used.tzinfo is None:
            last_used = last_used.replace(tzinfo=timezone.utc)
        if (now - last_used).total_seconds() < _LAST_USED_THROTTLE_SECONDS:
            return
    token.last_used_at = now
    session.add(token)
    await session.commit()
