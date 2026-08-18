"""Authentication for the MCP surface (Phase 11 / ADR-0019).

Two independent dependencies, never merged into one - the bootstrap
credential and a persistent McpToken authorize categorically different
things (01_SPEC.md SS4.3):

- ``require_bootstrap_auth`` - a normal FastAPI dependency, used only by
  ``POST /api/mcp/tokens`` (api/routes/mcp_tokens.py). Accepts the bootstrap
  token. Never wired into any ``/mcp`` route.
- ``McpBearerAuthMiddleware`` - ASGI middleware wrapping the mounted
  ``/mcp`` Streamable HTTP app. Accepts only persistent, non-revoked
  McpToken-table tokens - never the bootstrap token, no fallback branch that
  checks it.

Implementation note (see ADR-0019 SS4): the MCP SDK's
``MCPServer.streamable_http_app()`` returns a plain Starlette ASGI app with
no FastAPI dependency-injection surface - tool handlers are plain functions,
not FastAPI routes. ``03_BACKEND.md`` SS3 originally sketched
``require_mcp_auth``/``require_scope`` as ``Depends(...)``-shaped; the
enforcement guarantee (every request authenticated before any MCP protocol
processing; every tool call scope-checked before it runs) is preserved, only
the mechanism is adapted: authentication is ASGI middleware, and
``require_scope`` becomes a plain function Milestone 2's tool handlers call
explicitly. This adaptation was pre-approved as part of Milestone 1's
authorization - see IMPLEMENT.md.
"""

from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Depends, Header
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import get_settings
from app.core.errors import ForbiddenError, UnauthorizedError
from app.database.session import get_sessionmaker
from app.services.mcp import tokens as tokens_service
from app.services.mcp.tokens import McpTokenContext


def _extract_bearer(header_value: str | None) -> str | None:
    if not header_value or not header_value.startswith("Bearer "):
        return None
    token = header_value.removeprefix("Bearer ").strip()
    return token or None


async def require_bootstrap_auth(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Used ONLY by POST /api/mcp/tokens. mcp_bootstrap_enabled is a true
    kill switch, checked before any token comparison - once false, even a
    correct bootstrap token is rejected (01_SPEC.md SS4.3)."""
    settings = get_settings()
    if not settings.mcp_bootstrap_enabled:
        raise UnauthorizedError("MCP bootstrap provisioning is disabled")
    token = _extract_bearer(authorization)
    expected = settings.resolved_mcp_bootstrap_token
    # hmac.compare_digest, not `!=` - constant-time comparison, matching
    # verify_session_token's pattern in app/core/security.py (MINOR finding,
    # Agentic Review M1: plain `!=` on a secret comparison is a timing-attack
    # surface, however small, and this codebase already has the right
    # primitive available).
    if not token or not expected or not hmac.compare_digest(token, expected):
        raise UnauthorizedError("Invalid bootstrap token")


RequireBootstrapAuth = Depends(require_bootstrap_auth)


def require_scope(ctx: McpTokenContext, scope: str) -> None:
    """Called explicitly by a tool handler body (Milestone 2 onward) - not
    wired into any transport-level dispatch, since FastMCP tools are plain
    functions. No tool in Milestone 1 calls this; it is defined now so
    Milestone 2 has a single, already-reviewed enforcement point rather than
    each tool inventing its own scope check."""
    if not ctx.has_scope(scope):
        raise ForbiddenError(f"MCP token lacks required scope: {scope}")


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


class McpBearerAuthMiddleware:
    """Raw ASGI middleware wrapping the mounted /mcp Streamable HTTP app.
    Rejects any request lacking a valid, non-revoked persistent McpToken
    before it reaches MCP protocol processing - including the initial
    handshake (AC3). The bootstrap token is never accepted here; there is no
    code path that checks it in this class."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        token = _extract_bearer(headers.get("authorization"))
        if token is None:
            await _error_response(401, "unauthorized", "Missing MCP bearer token")(scope, receive, send)
            return

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            ctx = await tokens_service.verify(session, token)
            if ctx is None:
                await _error_response(401, "unauthorized", "Invalid or revoked MCP token")(scope, receive, send)
                return
            await tokens_service.touch_last_used(session, ctx.token_id)

        scope.setdefault("state", {})["mcp_token_context"] = ctx
        await self.app(scope, receive, send)
