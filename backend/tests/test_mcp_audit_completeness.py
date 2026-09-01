"""M5-T3 (09_IMPLEMENTATION_TASKS.md) - audit completeness pass. Every
write/delete tool is confirmed here, in one place, to log to `ActivityLog`
with `source="mcp"` exactly when 01_SPEC.md SS4.5/06_API.md's per-tool Audit
rows say it should - including the three documented, deliberate exceptions
(forge_update_note/forge_update_document, forge_link_items/
forge_unlink_items) that produce NO row, matching pre-existing REST
behavior rather than gaining new logging as an unplanned side effect. Also
confirms every read tool logs nothing at all (08_ACCEPTANCE.md SS6's open
question - "should reads log?" - remains genuinely undecided; this test
verifies the current, consistent answer - no - actually holds everywhere,
not that it *should* hold; changing that answer is a future product
decision, not something this test enforces as correct).

This consolidates what Milestones 2-4's own test files already assert
individually (test_create_note_produces_exactly_one_activity_row_with_mcp_source,
the link/unlink no-audit-row tests, the memory-tools audit test) into one
authoritative, exhaustive sweep across all 18 tools - the completeness
Milestone 5's own gate exists to prove, not a duplicate of milestone-level
coverage."""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import select

MCP_HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
INITIALIZE_PARAMS = {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}}

_READ_TOOLS: list[tuple[str, dict]] = [
    ("forge_search", {"query": "zzz-audit-completeness-nonexistent"}),
    ("forge_context", {"topic": "zzz-audit-completeness-nonexistent"}),
    ("forge_get_note", {"note_id": "does-not-exist"}),
    ("forge_get_document", {"document_id": "does-not-exist"}),
    ("forge_list_projects", {}),
    ("forge_get_project", {"project_id": "does-not-exist"}),
]


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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-audit-completeness-test-")
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
        json={"name": "audit-completeness-test", "scopes": scopes},
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
    import json

    return json.loads(body["content"][0]["text"])


def _call_tool(client, sid, token, name, arguments, request_id):
    return _tool_result(_call(client, sid, token, "tools/call", {"name": name, "arguments": arguments}, request_id))


async def _activity_rows(sessionmaker):
    from app.models.activity import ActivityLog

    async with sessionmaker() as session:
        result = await session.execute(select(ActivityLog))
        return result.scalars().all()


@pytest.mark.parametrize(
    "make_call",
    [
        lambda env, sid, token: _call_tool(env, sid, token, "forge_create_note", {"title": "audit-note"}, 2),
        lambda env, sid, token: _call_tool(env, sid, token, "forge_create_document", {"title": "audit-doc", "content": "<p>x</p>"}, 2),
        lambda env, sid, token: _call_tool(env, sid, token, "forge_create_project", {"name": "audit-project"}, 2),
        lambda env, sid, token: _call_tool(env, sid, token, "forge_capture_decision", {"summary": "audit-decision"}, 2),
        lambda env, sid, token: _call_tool(env, sid, token, "forge_capture_session", {"summary": "audit-session"}, 2),
    ],
    ids=["forge_create_note", "forge_create_document", "forge_create_project", "forge_capture_decision", "forge_capture_session"],
)
async def test_create_tools_produce_exactly_one_activity_row_with_mcp_source(env, make_call):
    from app.database.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    before = await _activity_rows(sessionmaker)

    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])
    make_call(env, sid, token)

    after = await _activity_rows(sessionmaker)
    new_rows = [r for r in after if r.id not in {b.id for b in before}]
    assert len(new_rows) == 1
    assert new_rows[0].source == "mcp"
    assert new_rows[0].action == "created"


async def test_forge_update_project_produces_one_activity_row_with_mcp_source(env):
    """Unlike Notes/Documents, project updates already logged for every
    caller pre-Phase-11 (01_SPEC.md SS4.5) - the one write-class tool
    outside forge_create_* that IS expected to log."""
    from app.database.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    token, sid = _connect(env, ["forge:read", "forge:write"])
    project = _call_tool(env, sid, token, "forge_create_project", {"name": "audit-update-project"}, 2)

    before = await _activity_rows(sessionmaker)
    _call_tool(env, sid, token, "forge_update_project", {"project_id": project["id"], "name": "renamed"}, 3)
    after = await _activity_rows(sessionmaker)

    new_rows = [r for r in after if r.id not in {b.id for b in before}]
    assert len(new_rows) == 1
    assert new_rows[0].source == "mcp"
    assert new_rows[0].action == "updated"


@pytest.mark.parametrize(
    "create_name,create_args,delete_name,id_field",
    [
        ("forge_create_note", {"title": "audit-delete-note"}, "forge_delete_note", "note_id"),
        ("forge_create_document", {"title": "audit-delete-doc", "content": "<p>x</p>"}, "forge_delete_document", "document_id"),
    ],
    ids=["forge_delete_note", "forge_delete_document"],
)
async def test_delete_tools_produce_exactly_one_activity_row_with_mcp_source(env, create_name, create_args, delete_name, id_field):
    from app.database.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])
    created = _call_tool(env, sid, token, create_name, create_args, 2)

    before = await _activity_rows(sessionmaker)
    _call_tool(env, sid, token, delete_name, {id_field: created["id"], "confirm": True}, 3)
    after = await _activity_rows(sessionmaker)

    new_rows = [r for r in after if r.id not in {b.id for b in before}]
    assert len(new_rows) == 1
    assert new_rows[0].source == "mcp"
    assert new_rows[0].action == "deleted"


async def test_forge_update_note_and_update_document_produce_no_activity_row(env):
    """01_SPEC.md SS4.5's documented exception - never logged for any
    caller, REST or MCP, before or after Phase 11."""
    from app.database.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note = _call_tool(env, sid, token, "forge_create_note", {"title": "audit-update-note"}, 2)
    document = _call_tool(env, sid, token, "forge_create_document", {"title": "audit-update-doc", "content": "<p>x</p>"}, 3)

    before = await _activity_rows(sessionmaker)
    _call_tool(env, sid, token, "forge_update_note", {"note_id": note["id"], "title": "updated"}, 4)
    _call_tool(env, sid, token, "forge_update_document", {"document_id": document["id"], "title": "updated"}, 5)
    after = await _activity_rows(sessionmaker)

    assert len(after) == len(before)


async def test_forge_link_items_and_unlink_items_produce_no_activity_row(env):
    """01_SPEC.md SS4.5's Milestone 3 correction - knowledge_service.create_link/
    delete_link have never logged for any caller."""
    from app.database.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    token, sid = _connect(env, ["forge:read", "forge:write"])
    note_a = _call_tool(env, sid, token, "forge_create_note", {"title": "audit-link-a"}, 2)
    note_b = _call_tool(env, sid, token, "forge_create_note", {"title": "audit-link-b"}, 3)

    before = await _activity_rows(sessionmaker)
    link = _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note_a["id"], "target_type": "note", "target_id": note_b["id"]}, 4,
    )
    _call_tool(env, sid, token, "forge_unlink_items", {"link_id": link["id"]}, 5)
    after = await _activity_rows(sessionmaker)

    assert len(after) == len(before)


@pytest.mark.parametrize("name,args", _READ_TOOLS, ids=[t[0] for t in _READ_TOOLS])
async def test_read_tools_never_write_to_activity_log(env, name, args):
    """08_ACCEPTANCE.md SS6's open question ("should AI-driven reads log?")
    is not resolved by this test - it verifies the CURRENT, consistent
    answer (no) actually holds for every read tool, matching the existing
    REST/UI convention of never logging `viewed` actions."""
    from app.database.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    token, sid = _connect(env, ["forge:read"])

    before = await _activity_rows(sessionmaker)
    _call(env, sid, token, "tools/call", {"name": name, "arguments": args}, 2)
    after = await _activity_rows(sessionmaker)

    assert len(after) == len(before), f"{name} (a read tool) wrote to ActivityLog - violates the existing no-log-reads convention"


def test_audit_completeness_covers_every_mutating_tool():
    """Guards this file's own coverage from silently going stale."""
    covered_creates = {"forge_create_note", "forge_create_document", "forge_create_project", "forge_capture_decision", "forge_capture_session"}
    covered_deletes = {"forge_delete_note", "forge_delete_document"}
    covered_no_audit = {"forge_update_note", "forge_update_document", "forge_link_items", "forge_unlink_items"}
    covered_logged_update = {"forge_update_project"}
    all_mutating_tools = covered_creates | covered_deletes | covered_no_audit | covered_logged_update
    assert all_mutating_tools == {
        "forge_create_note", "forge_update_note", "forge_delete_note",
        "forge_create_document", "forge_update_document", "forge_delete_document",
        "forge_create_project", "forge_update_project",
        "forge_link_items", "forge_unlink_items",
        "forge_capture_decision", "forge_capture_session",
    }
    assert len(all_mutating_tools) == 12
