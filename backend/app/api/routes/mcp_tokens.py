"""POST/GET/DELETE /api/mcp/tokens - provisions, lists, and revokes
persistent MCP bearer tokens (01_SPEC.md SS4.3.1). A REST route, not an MCP
tool - provisioning is an administrative action the human owner takes
(browser session, or the bootstrap token for headless first-run setup),
never something Claude calls on itself."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header

from app.api.deps import SessionDep, require_auth
from app.core.errors import AppError, NotFoundError
from app.mcp.auth import require_bootstrap_auth
from app.schemas.mcp_tokens import McpTokenCreatedOut, McpTokenCreateIn, McpTokenOut
from app.services.mcp import tokens as tokens_service

router = APIRouter(prefix="/mcp/tokens", tags=["mcp-tokens"])


async def _require_session_or_bootstrap(
    session: SessionDep,
    forge_session: Annotated[str | None, Cookie()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Accepts EITHER a valid browser session OR a valid, enabled bootstrap
    token - applies uniformly to all three routes below, so a fully headless
    first-run script (bootstrap token, no browser session yet) can
    provision, list, and revoke tokens before any human ever unlocks the UI.
    FastAPI has no built-in "OR" dependency combinator; this tries the
    session first and only checks the bootstrap token if that fails.

    The `forge_session` cookie is declared here (not left to require_auth's
    own signature) and passed through explicitly - calling require_auth(...)
    without going through FastAPI's own dependency-injection call would leave
    its Cookie()-marked parameter unresolved (always None), silently making
    every session check fail regardless of whether a valid cookie was sent.
    Caught by an independent Agentic Review during the Milestone 1 gate
    (BLOCKER: cookie-based provisioning was dead code) - see
    reviews/AGENTIC_REVIEW_M1.md and test_mcp_tokens_api.py's
    test_browser_session_alone_can_provision_a_token regression test.

    Catches AppError broadly (not just UnauthorizedError) because
    require_auth also raises SetupRequiredError when first-run setup hasn't
    happened yet - the bootstrap path must still work in that case, since it
    has no dependency on the master password at all (only on
    FORGE_MASTER_KEY, via resolved_mcp_bootstrap_token), which is exactly the
    headless-first-run scenario this route exists for."""
    try:
        await require_auth(session, forge_session)
        return
    except AppError:
        pass
    await require_bootstrap_auth(authorization)


RequireSessionOrBootstrap = Depends(_require_session_or_bootstrap)


@router.post("", response_model=McpTokenCreatedOut, status_code=201, dependencies=[RequireSessionOrBootstrap])
async def create_token(body: McpTokenCreateIn, session: SessionDep) -> McpTokenCreatedOut:
    token, raw = await tokens_service.issue(session, name=body.name, scopes=body.scopes)
    out = McpTokenOut.from_model(token)
    return McpTokenCreatedOut(**out.model_dump(), token=raw)


@router.get("", response_model=list[McpTokenOut], dependencies=[RequireSessionOrBootstrap])
async def list_tokens(session: SessionDep) -> list[McpTokenOut]:
    tokens = await tokens_service.list_tokens(session)
    return [McpTokenOut.from_model(t) for t in tokens]


@router.delete("/{token_id}", status_code=204, dependencies=[RequireSessionOrBootstrap])
async def revoke_token(token_id: str, session: SessionDep) -> None:
    token = await tokens_service.revoke(session, token_id)
    if token is None:
        raise NotFoundError("MCP token not found")
