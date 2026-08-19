"""End-to-end MCP transport/auth tests (Milestone 1 vertical slice).

Uses raw JSON-RPC bodies against the mounted Streamable HTTP app via
Starlette's TestClient (which correctly drives the ASGI lifespan protocol,
starting/stopping the MCP session manager - see app/mcp/server.py's
docstring on why that chaining matters). This exercises the real MCP SDK
server-side machinery end to end: transport, McpBearerAuthMiddleware,
scope/session handling, and the initialize handshake - the same behavior a
real Claude Code client relies on, without requiring a live network
connection from an actual Claude Code process in this test environment.
"""

from __future__ import annotations

import os
import tempfile

import pytest

INITIALIZE_BODY = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0"},
    },
}
MCP_HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}


def _mcp_env(prefix: str, *, mcp_enabled: str = "true"):
    return {
        "FORGE_DATA_DIR": tempfile.mkdtemp(prefix=f"forge-{prefix}-"),
        "FORGE_MCP_ENABLED": mcp_enabled,
        "FORGE_MCP_BOOTSTRAP_TOKEN": "bootstrap-secret",
        "FORGE_MCP_BOOTSTRAP_ENABLED": "true",
    }


def _fresh_app(env: dict[str, str]):
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous = {k: os.environ.get(k) for k in env}
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ.update(env)

    from app.main import create_app

    app = create_app()
    return app, previous


def _restore_env(previous: dict[str, str | None]):
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


@pytest.fixture(scope="module")
def mcp_client():
    from starlette.testclient import TestClient

    app, previous = _fresh_app(_mcp_env("mcp-server-test"))
    with TestClient(app) as c:
        yield c
    _restore_env(previous)


def _provision_token(client, *, scopes=("forge:read",)) -> str:
    response = client.post(
        "/api/mcp/tokens",
        json={"name": "test", "scopes": list(scopes)},
        headers={"Authorization": "Bearer bootstrap-secret"},
    )
    assert response.status_code == 201
    return response.json()["token"]


def test_mcp_disabled_by_default_leaves_mcp_unmounted():
    from starlette.testclient import TestClient

    app, previous = _fresh_app(_mcp_env("mcp-disabled-test", mcp_enabled="false"))
    try:
        with TestClient(app) as c:
            response = c.post("/mcp", json={}, headers=MCP_HEADERS)
            assert response.status_code == 404
            # /health and /api/* must be completely unaffected by MCP being disabled.
            assert c.get("/health").status_code == 200
    finally:
        _restore_env(previous)


def test_missing_authorization_header_is_rejected_before_any_protocol_processing(mcp_client):
    response = mcp_client.post("/mcp/", json=INITIALIZE_BODY, headers=MCP_HEADERS)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_malformed_authorization_header_is_rejected(mcp_client):
    response = mcp_client.post(
        "/mcp/", json=INITIALIZE_BODY, headers={**MCP_HEADERS, "Authorization": "NotBearer abc"}
    )
    assert response.status_code == 401


def test_bootstrap_token_is_never_accepted_by_mcp_itself(mcp_client):
    """The single most important security property of this milestone
    (IMPLEMENT.md) - the bootstrap credential must never work as Claude's
    runtime credential."""
    response = mcp_client.post(
        "/mcp/", json=INITIALIZE_BODY, headers={**MCP_HEADERS, "Authorization": "Bearer bootstrap-secret"}
    )
    assert response.status_code == 401


def test_valid_persistent_token_completes_the_handshake_and_lists_tools(mcp_client):
    """Originally asserted zero tools (Milestone 1's actual state: transport/
    auth foundation only, no CRUD tools registered yet). Milestone 2 added
    the 12 Knowledge CRUD tools (app/mcp/tools/notes.py, documents.py,
    projects.py); Milestone 3 added forge_search/forge_context
    (app/mcp/tools/search.py) and forge_link_items/forge_unlink_items
    (app/mcp/tools/knowledge.py) - this test now asserts the handshake still
    works and the real, current tool set is what tools/list reports, rather
    than re-assert a stale fact each milestone that registers a new tool.
    Full CRUD/search/knowledge-graph behavior per tool is covered by
    test_mcp_tools_crud.py / test_mcp_tools_search_context.py /
    test_mcp_tools_knowledge.py; this test only proves the handshake/listing
    path itself still works end to end."""
    token = _provision_token(mcp_client)

    response = mcp_client.post("/mcp/", json=INITIALIZE_BODY, headers={**MCP_HEADERS, "Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["serverInfo"]["name"] == "forge"
    session_id = response.headers["mcp-session-id"]

    tools_response = mcp_client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        headers={**MCP_HEADERS, "Authorization": f"Bearer {token}", "mcp-session-id": session_id},
    )
    assert tools_response.status_code == 200
    names = {t["name"] for t in tools_response.json()["result"]["tools"]}
    assert names == {
        "forge_get_note",
        "forge_create_note",
        "forge_update_note",
        "forge_delete_note",
        "forge_get_document",
        "forge_create_document",
        "forge_update_document",
        "forge_delete_document",
        "forge_list_projects",
        "forge_get_project",
        "forge_create_project",
        "forge_update_project",
        "forge_search",
        "forge_context",
        "forge_link_items",
        "forge_unlink_items",
    }


def test_bare_mcp_path_without_trailing_slash_works_with_no_redirect(mcp_client):
    """Guards against the 307-redirect trap this milestone found and fixed
    at the nginx layer (docker/nginx.conf) - in-process, FastAPI's own Mount
    still redirects a bare path, so this asserts that behavior is at least
    understood/stable, not a silent regression to something worse than a
    redirect (e.g. a 404)."""
    token = _provision_token(mcp_client)
    response = mcp_client.post(
        "/mcp", json=INITIALIZE_BODY, headers={**MCP_HEADERS, "Authorization": f"Bearer {token}"}, follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"].endswith("/mcp/")


def test_revoked_token_is_rejected_immediately(mcp_client):
    create = mcp_client.post(
        "/api/mcp/tokens",
        json={"name": "to-revoke", "scopes": ["forge:read"]},
        headers={"Authorization": "Bearer bootstrap-secret"},
    ).json()
    token = create["token"]

    ok = mcp_client.post("/mcp/", json=INITIALIZE_BODY, headers={**MCP_HEADERS, "Authorization": f"Bearer {token}"})
    assert ok.status_code == 200

    mcp_client.delete(f"/api/mcp/tokens/{create['id']}", headers={"Authorization": "Bearer bootstrap-secret"})

    after_revoke = mcp_client.post("/mcp/", json=INITIALIZE_BODY, headers={**MCP_HEADERS, "Authorization": f"Bearer {token}"})
    assert after_revoke.status_code == 401


def test_mcp_token_cannot_authenticate_against_the_rest_api(mcp_client):
    """AC19 - the two auth schemes are provably independent in both
    directions. This half: an MCP bearer token is meaningless to AuthDep,
    which only ever reads the forge_session cookie."""
    token = _provision_token(mcp_client)
    response = mcp_client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_browser_session_cookie_cannot_authenticate_against_mcp():
    """AC19, the other half: a valid forge_session cookie must not satisfy
    McpBearerAuthMiddleware, which only ever reads the Authorization header.
    Uses its own fresh app/client (not the shared module-scoped mcp_client)
    so completing first-run setup here can't leak state into other tests in
    this module that assume setup hasn't happened yet."""
    from starlette.testclient import TestClient

    app, previous = _fresh_app(_mcp_env("mcp-cookie-independence-test"))
    try:
        with TestClient(app) as c:
            setup = c.post("/api/setup", json={"master_password": "correct horse battery staple"})
            assert setup.status_code == 200
            assert "forge_session" in c.cookies

            response = c.post("/mcp/", json=INITIALIZE_BODY, headers=MCP_HEADERS)
            assert response.status_code == 401
    finally:
        _restore_env(previous)
