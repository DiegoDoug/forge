"""End-to-end MCP tests for forge_capture_decision/forge_capture_session
(Milestone 4). Same real-JSON-RPC-through-the-mounted-app pattern as
test_mcp_tools_knowledge.py."""

from __future__ import annotations

import json
import os
import tempfile

import pytest
from sqlalchemy import select

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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-memory-test-")
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


def _connect(client, scopes):
    token = client.post(
        "/api/mcp/tokens",
        json={"name": "test", "scopes": scopes},
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


def _tool_error(response) -> str:
    body = response.json()["result"]
    assert body.get("isError"), body
    return body["content"][0]["text"]


def _call_tool(client, sid, token, name, arguments, request_id):
    return _tool_result(_call(client, sid, token, "tools/call", {"name": name, "arguments": arguments}, request_id))


def test_forge_capture_decision_creates_a_tagged_note(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(env, sid, token, "forge_capture_decision", {"summary": "Use SQLite over Postgres"}, 2)
    assert note["title"] == "Decision: Use SQLite over Postgres"
    assert [t["name"] for t in note["tags"]] == ["ai-decision"]


def test_forge_capture_session_creates_a_dated_tagged_note(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(env, sid, token, "forge_capture_session", {"summary": "Shipped Milestone 4"}, 2)
    assert note["title"].startswith("Session ")
    assert note["title"].endswith(": Shipped Milestone 4")
    assert [t["name"] for t in note["tags"]] == ["ai-session"]


def test_forge_capture_decision_stores_detail_as_note_body(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(
        env, sid, token, "forge_capture_decision",
        {"summary": "Adopt scope-per-tool auth", "detail": "Rejected connection-level-only auth - see 01_SPEC.md SS4.4."},
        2,
    )
    assert note["content"] == "Rejected connection-level-only auth - see 01_SPEC.md SS4.4."


def test_forge_capture_decision_reuses_the_same_reserved_tag_across_calls(env):
    """Reserved tags are the pre-existing shared tags vocabulary
    (knowledge_service.add_tag's create-or-reuse-by-name behavior) - two
    captured decisions must share one 'ai-decision' Tag row, not create a
    duplicate each time."""
    token, sid = _connect(env, ["forge:read", "forge:write"])
    first = _call_tool(env, sid, token, "forge_capture_decision", {"summary": "First decision"}, 2)
    second = _call_tool(env, sid, token, "forge_capture_decision", {"summary": "Second decision"}, 3)
    assert first["tags"][0]["id"] == second["tags"][0]["id"]


def test_forge_capture_decision_and_session_are_found_by_forge_search(env):
    """08_ACCEPTANCE.md AC14/AC15's discoverability requirement, exercised
    within a single session here - the cross-session half is
    test_mcp_memory_continuity.py's job."""
    token, sid = _connect(env, ["forge:read", "forge:write"])
    _call_tool(env, sid, token, "forge_capture_decision", {"summary": "unique-marker-zephyr choose FastAPI"}, 2)

    results = _call_tool(env, sid, token, "forge_search", {"query": "unique-marker-zephyr"}, 3)
    assert any(r["title"] == "Decision: unique-marker-zephyr choose FastAPI" for r in results)


async def test_forge_capture_decision_produces_exactly_one_activity_row_with_mcp_source(env):
    """Matches 06_API.md SS4's Audit row - create_note's own activity.record
    call logs once; add_tag must not log a second time (it never has, for
    any caller - services/knowledge/service.py::add_tag has no
    activity.record call at all)."""
    from app.database.session import get_sessionmaker
    from app.models.activity import ActivityLog

    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(env, sid, token, "forge_capture_decision", {"summary": "audit-marker decision"}, 2)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await session.execute(select(ActivityLog).where(ActivityLog.entity_id == note["id"]))
        rows = result.scalars().all()

    assert len(rows) == 1
    assert rows[0].source == "mcp"
    assert rows[0].action == "created"


def test_forge_capture_decision_rejects_summary_over_180_chars(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    error = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_capture_decision", "arguments": {"summary": "x" * 181}}, 2)
    )
    assert "180" in error


def test_forge_capture_decision_rejects_empty_summary(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    error = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_capture_decision", "arguments": {"summary": "   "}}, 2)
    )
    assert "180" in error or "1-" in error


def test_forge_capture_decision_and_session_require_forge_write(env):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_capture_decision", "arguments": {"summary": "x"}}, 2)
    )
    assert "scope" in error.lower()

    error2 = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_capture_session", "arguments": {"summary": "x"}}, 3)
    )
    assert "scope" in error2.lower()


def test_forge_capture_decision_unknown_project_id_errors(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {"name": "forge_capture_decision", "arguments": {"summary": "x", "project_id": "does-not-exist"}},
            2,
        )
    )
    assert "not found" in error.lower()
