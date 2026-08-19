"""AC14 (08_ACCEPTANCE.md SS4) - cross-session continuity. A decision
captured via forge_capture_decision in one Claude session must be
retrievable via forge_search/forge_context in a later, INDEPENDENT Claude
session - proving memory capture is genuinely integrated into the knowledge
substrate (persisted to the real SQLite DB, indexed in notes_fts like any
other note) rather than merely round-tripping within a single MCP
connection's lifetime.

"Independent session" here means a fresh MCP protocol session: its own
`initialize` handshake, its own `mcp-session-id`, and (to rule out any
session-scoped in-memory state on the token/scope path too) its own
separately-provisioned persistent token - not the same connection reused
with a second request. Milestone 4's Agentic Review gate re-runs this
independently (09_IMPLEMENTATION_TASKS.md's Milestone 4 gate)."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

MCP_HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
INITIALIZE_PARAMS = {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}}


def _fresh_app():
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous = {
        k: os.environ.get(k)
        for k in ("FORGE_DATA_DIR", "FORGE_MCP_ENABLED", "FORGE_MCP_BOOTSTRAP_TOKEN", "FORGE_MCP_BOOTSTRAP_ENABLED")
    }
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-continuity-test-")
    os.environ["FORGE_MCP_ENABLED"] = "true"
    os.environ["FORGE_MCP_BOOTSTRAP_TOKEN"] = "bootstrap-secret"
    os.environ["FORGE_MCP_BOOTSTRAP_ENABLED"] = "true"

    from app.main import create_app

    return create_app(), previous


def _restore_env(previous):
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
def env():
    from starlette.testclient import TestClient

    app, previous = _fresh_app()
    with TestClient(app) as c:
        yield c
    _restore_env(previous)


def _call(client, session_id, token, method, params, request_id=1):
    headers = {**MCP_HEADERS, "Authorization": f"Bearer {token}"}
    if session_id:
        headers["mcp-session-id"] = session_id
    return client.post("/mcp/", json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}, headers=headers)


def _new_independent_session(client, *, token_name: str, scopes: list[str]):
    """A fresh persistent token AND a fresh `initialize` handshake - the
    strongest sense of "a different Claude session" this test harness can
    express without a second live process."""
    token = client.post(
        "/api/mcp/tokens",
        json={"name": token_name, "scopes": scopes},
        headers={"Authorization": "Bearer bootstrap-secret"},
    ).json()["token"]
    init = _call(client, None, token, "initialize", INITIALIZE_PARAMS)
    assert init.status_code == 200
    return token, init.headers["mcp-session-id"]


def _tool_result(response):
    body = response.json()["result"]
    assert not body.get("isError"), body
    structured = body.get("structuredContent")
    if structured is not None:
        if set(structured.keys()) == {"result"}:
            return structured["result"]
        return structured
    return json.loads(body["content"][0]["text"])


def _call_tool(client, sid, token, name, arguments, request_id):
    return _tool_result(_call(client, sid, token, "tools/call", {"name": name, "arguments": arguments}, request_id))


def test_decision_captured_in_one_session_is_found_by_forge_search_in_a_second_independent_session(env):
    write_token, write_sid = _new_independent_session(env, token_name="session-one-writer", scopes=["forge:write"])
    captured = _call_tool(
        env, write_sid, write_token, "forge_capture_decision",
        {"summary": "continuity-marker-lighthouse adopt Streamable HTTP"}, 2,
    )

    read_token, read_sid = _new_independent_session(env, token_name="session-two-reader", scopes=["forge:read"])
    results = _call_tool(env, read_sid, read_token, "forge_search", {"query": "continuity-marker-lighthouse"}, 2)

    assert any(r["id"] == captured["id"] and r["type"] == "note" for r in results)


def test_decision_captured_in_one_session_is_found_by_forge_context_in_a_second_independent_session(env):
    write_token, write_sid = _new_independent_session(env, token_name="session-three-writer", scopes=["forge:write"])
    captured = _call_tool(
        env, write_sid, write_token, "forge_capture_session",
        {"summary": "continuity-marker-harbor migrated to Streamable HTTP"}, 2,
    )

    read_token, read_sid = _new_independent_session(env, token_name="session-four-reader", scopes=["forge:read"])
    context = _call_tool(env, read_sid, read_token, "forge_context", {"topic": "continuity-marker-harbor"}, 2)

    assert any(n["id"] == captured["id"] for n in context["notes"])
    assert any(t["name"] == "ai-session" for n in context["notes"] for t in n["tags"] if n["id"] == captured["id"])
