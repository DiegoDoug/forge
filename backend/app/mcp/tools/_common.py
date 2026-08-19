"""Shared helpers for MCP tool handlers - not a verifier-agnostic-style
"no cross-imports" package (unlike tools/fdk_verification/verifiers/), since
every tool handler legitimately needs the same two things: a DB session and
the calling token's scope context."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.mcpserver import Context
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError
from app.database.session import get_sessionmaker
from app.mcp.auth import _extract_bearer
from app.services.mcp import tokens as tokens_service
from app.services.mcp.tokens import McpTokenContext
from app.services.projects import service as projects_service


@asynccontextmanager
async def tool_session() -> AsyncIterator[AsyncSession]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


async def validate_project_id(session: AsyncSession, project_id: str | None) -> None:
    """Confirms project_id (if given) actually exists before it's handed to
    notes_service/documents_service, which would otherwise fail deep inside
    a DB flush with an unhandled `sqlite3.IntegrityError` - one that reached
    the tool caller as a raw, unmapped exception carrying the full SQL
    statement and the submitted note/document content (Milestone 2 Agentic
    Review MAJOR finding). Raises the existing, clean NotFoundError instead,
    matching 06_API.md's documented "unknown project_id -> not-found error,
    not a silently-orphaned note" contract. A no-op when project_id is None."""
    if project_id is None:
        return
    await projects_service.get_project(session, project_id)


def filtered_update_kwargs(**kwargs) -> dict:
    """Only fields the caller actually supplied become part of a partial
    update - a value of None is treated as "not supplied," matching how a
    flat MCP tool-argument surface (no distinct "omitted" vs "explicitly
    null" signal once mapped to Python keyword defaults) can express partial
    updates. Documented v1 limitation, shared by every *_update_* tool: this
    surface cannot explicitly null out a nullable field (e.g. un-scope an
    item from its project by setting project_id to null) - a caller who
    wants that must currently do it through the existing REST/UI path."""
    return {k: v for k, v in kwargs.items() if v is not None}


async def current_scope(ctx: Context, session: AsyncSession) -> McpTokenContext:
    """Re-derives the calling token's scope context from the current tool
    call's HTTP Authorization header (Context.headers - the MCP SDK's own
    documented mechanism for a tool to reach the current request's headers).

    Deliberately independent of McpBearerAuthMiddleware's own verification,
    which already ran and is why this tool call reached this far at all -
    relying on ASGI scope state the middleware set would depend on
    undocumented propagation behavior through the SDK's internal
    session/dispatch layers, whereas ctx.headers is the supported surface.
    The extra indexed DB lookup this causes (one more `token_hash` exact
    match per tool call) is cheap and worth the simplicity/correctness
    tradeoff - see app/mcp/auth.py's module docstring for the same
    reasoning applied to the transport-level check."""
    headers = ctx.headers or {}
    token = _extract_bearer(headers.get("authorization"))
    if token is None:
        raise UnauthorizedError("Missing MCP bearer token")
    token_ctx = await tokens_service.verify(session, token)
    if token_ctx is None:
        raise UnauthorizedError("Invalid or revoked MCP token")
    return token_ctx
