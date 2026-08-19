"""End-to-end MCP tests for forge_link_items/forge_unlink_items (Milestone
3). Same pattern as test_mcp_tools_crud.py."""

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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-knowledge-test-")
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


def test_forge_link_items_creates_and_forge_unlink_items_removes(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note_a = _call_tool(env, sid, token, "forge_create_note", {"title": "A"}, 2)
    note_b = _call_tool(env, sid, token, "forge_create_note", {"title": "B"}, 3)

    link = _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note_a["id"], "target_type": "note", "target_id": note_b["id"]}, 4,
    )
    assert link["source_type"] == "note" and link["source_id"] == note_a["id"]
    assert link["target_type"] == "note" and link["target_id"] == note_b["id"]

    unlinked = _call_tool(env, sid, token, "forge_unlink_items", {"link_id": link["id"]}, 5)
    assert unlinked == {"unlinked": True, "id": link["id"]}

    again = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_unlink_items", "arguments": {"link_id": link["id"]}}, 6)
    )
    assert "not found" in again.lower()


def test_forge_link_items_relink_either_direction_returns_existing_link_not_an_error(env):
    """07_TESTING.md SS2 - relinking an already-linked pair (in either
    direction) must return the existing link, not surface the service's
    own duplicate-row-prevention error. See app/mcp/tools/knowledge.py's
    comment for why the underlying service raises a 409 here that this
    tool must catch and translate."""
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note_a = _call_tool(env, sid, token, "forge_create_note", {"title": "A"}, 2)
    note_b = _call_tool(env, sid, token, "forge_create_note", {"title": "B"}, 3)

    first = _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note_a["id"], "target_type": "note", "target_id": note_b["id"]}, 4,
    )
    same_direction = _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note_a["id"], "target_type": "note", "target_id": note_b["id"]}, 5,
    )
    assert same_direction["id"] == first["id"]

    reverse_direction = _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note_b["id"], "target_type": "note", "target_id": note_a["id"]}, 6,
    )
    assert reverse_direction["id"] == first["id"]


def test_forge_link_items_self_link_rejected(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(env, sid, token, "forge_create_note", {"title": "A"}, 2)
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {
                "name": "forge_link_items",
                "arguments": {"source_type": "note", "source_id": note["id"], "target_type": "note", "target_id": note["id"]},
            },
            3,
        )
    )
    assert "itself" in error.lower()


def test_forge_link_items_unknown_item_errors(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(env, sid, token, "forge_create_note", {"title": "A"}, 2)
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {
                "name": "forge_link_items",
                "arguments": {
                    "source_type": "note", "source_id": note["id"],
                    "target_type": "document", "target_id": "does-not-exist",
                },
            },
            3,
        )
    )
    assert "not found" in error.lower()


def test_forge_link_items_invalid_item_type_rejected(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {
                "name": "forge_link_items",
                "arguments": {"source_type": "secret", "source_id": "x", "target_type": "note", "target_id": "y"},
            },
            2,
        )
    )
    assert "note" in error.lower() or "document" in error.lower()


async def test_forge_link_and_unlink_items_produce_no_activity_row_matching_existing_rest_behavior(env):
    """Documented exception (06_API.md's Audit rows for forge_link_items/
    forge_unlink_items, 01_SPEC.md SS4.5's Milestone 3 correction):
    knowledge_service.create_link/delete_link have never logged to
    ActivityLog for any caller, REST or MCP - proves the MCP path didn't
    silently introduce new logging behavior. Found by the Milestone 3
    Agentic Review (MAJOR) as an undocumented gap; now documented and
    tested, matching the update_note/update_document precedent."""
    from app.database.session import get_sessionmaker
    from app.models.activity import ActivityLog

    token, sid = _connect(env, ["forge:read", "forge:write"])
    note_a = _call_tool(env, sid, token, "forge_create_note", {"title": "AuditLinkA"}, 2)
    note_b = _call_tool(env, sid, token, "forge_create_note", {"title": "AuditLinkB"}, 3)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        before = (await session.execute(select(ActivityLog))).scalars().all()

    link = _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note_a["id"], "target_type": "note", "target_id": note_b["id"]}, 4,
    )
    async with sessionmaker() as session:
        after_link = (await session.execute(select(ActivityLog))).scalars().all()
    assert len(after_link) == len(before), "forge_link_items must not write an ActivityLog row"

    _call_tool(env, sid, token, "forge_unlink_items", {"link_id": link["id"]}, 5)
    async with sessionmaker() as session:
        after_unlink = (await session.execute(select(ActivityLog))).scalars().all()
    assert len(after_unlink) == len(before), "forge_unlink_items must not write an ActivityLog row"


def test_forge_link_and_unlink_items_require_forge_write(env):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {
                "name": "forge_link_items",
                "arguments": {"source_type": "note", "source_id": "x", "target_type": "note", "target_id": "y"},
            },
            2,
        )
    )
    assert "scope" in error.lower()

    error2 = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_unlink_items", "arguments": {"link_id": "x"}}, 3)
    )
    assert "scope" in error2.lower()
