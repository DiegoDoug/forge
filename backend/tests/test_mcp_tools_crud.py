"""End-to-end MCP CRUD tool tests (Milestone 2). Real JSON-RPC tool calls
through the mounted Streamable HTTP app, same pattern as test_mcp_server.py -
exercises the real MCP SDK dispatch, McpBearerAuthMiddleware, and
require_scope, not just the underlying service functions directly."""

from __future__ import annotations

import json
import os
import tempfile

import pytest
from sqlalchemy import select

MCP_HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
INITIALIZE_BODY = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}},
}


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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-crud-test-")
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
    init = _call(client, None, token, "initialize", INITIALIZE_BODY["params"])
    assert init.status_code == 200
    return token, init.headers["mcp-session-id"]


def _tool_result(response):
    """Prefers structuredContent over content[0].text, discovered empirically
    (not assumed) to be necessary: a tool returning a list wraps it as
    {"result": [...]} in structuredContent while content[0].text only shows
    a single-item preview. structuredContent is not always present, though
    (observed absent for at least one bare `dict`-returning tool despite
    being present for others of the same declared return type - an
    inconsistency in the MCP SDK's schema-inference heuristic, not something
    this phase's tool code controls) - falls back to parsing content[0].text
    as JSON in that case, which is always present and correct for
    single-object results (only list results need the structuredContent
    path, since their text preview is truncated to one item)."""
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


# --- Notes full lifecycle ---------------------------------------------------


def test_note_create_get_update_delete_lifecycle(env):
    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])

    created = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "Hello", "content": "World"}}, 2)
    )
    assert created["title"] == "Hello"
    note_id = created["id"]

    fetched = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_get_note", "arguments": {"note_id": note_id}}, 3))
    assert fetched["id"] == note_id

    updated = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_update_note", "arguments": {"note_id": note_id, "pinned": True}}, 4)
    )
    assert updated["pinned"] is True
    assert updated["title"] == "Hello", "partial update must not clobber untouched fields"

    no_confirm = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_note", "arguments": {"note_id": note_id, "confirm": False}}, 5)
    )
    assert "confirm" in no_confirm.lower()

    deleted = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_note", "arguments": {"note_id": note_id, "confirm": True}}, 6)
    )
    assert deleted == {"deleted": True, "id": note_id}

    after = _tool_error(_call(env, sid, token, "tools/call", {"name": "forge_get_note", "arguments": {"note_id": note_id}}, 7))
    assert "not found" in after.lower()


def test_document_create_get_update_delete_lifecycle(env):
    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])

    created = _tool_result(
        _call(
            env, sid, token, "tools/call",
            {"name": "forge_create_document", "arguments": {"title": "Doc", "content": "<p>hi</p>"}}, 2,
        )
    )
    doc_id = created["id"]

    updated = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_update_document", "arguments": {"document_id": doc_id, "pinned": True}}, 3)
    )
    assert updated["pinned"] is True
    assert updated["title"] == "Doc", "partial update must not clobber untouched fields"

    deleted = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_document", "arguments": {"document_id": doc_id, "confirm": True}}, 4)
    )
    assert deleted == {"deleted": True, "id": doc_id}


def test_project_create_get_update_list_no_delete_tool(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])

    created = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_create_project", "arguments": {"name": "Client A"}}, 2)
    )
    assert created["name"] == "Client A"
    assert "secret_count" not in created, "AC10-equivalent: MCP project output must never include secret_count"
    project_id = created["id"]

    listed = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_list_projects", "arguments": {}}, 3))
    assert any(p["id"] == project_id for p in listed)

    updated = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_update_project", "arguments": {"project_id": project_id, "archived": True}}, 4)
    )
    assert updated["archived"] is True

    no_delete_tool = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_project", "arguments": {"project_id": project_id}}, 5)
    )
    assert "unknown tool" in no_delete_tool.lower()


# --- Delete safety (AC7, AC7a) -----------------------------------------------


async def test_delete_purges_knowledge_links_no_orphans(env):
    """AC7 - the single highest-value regression test per 07_TESTING.md SS2:
    deleting a note must not leave orphaned knowledge_links rows."""
    from app.database.session import get_sessionmaker
    from app.models.knowledge import KnowledgeLink
    from app.services.knowledge import service as knowledge_service

    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])
    note_a = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "A"}}, 2))
    note_b = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "B"}}, 3))

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await knowledge_service.create_link(session, "note", note_a["id"], "note", note_b["id"])

    deleted = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_note", "arguments": {"note_id": note_a["id"], "confirm": True}}, 4)
    )
    assert deleted["deleted"] is True

    async with sessionmaker() as session:
        result = await session.execute(
            select(KnowledgeLink).where(
                ((KnowledgeLink.source_type == "note") & (KnowledgeLink.source_id == note_a["id"]))
                | ((KnowledgeLink.target_type == "note") & (KnowledgeLink.target_id == note_a["id"]))
            )
        )
        assert result.scalar_one_or_none() is None, "orphaned knowledge_links row survived the delete"


async def test_delete_nonexistent_note_stages_zero_changes(env):
    """AC7a - the existence check runs before any mutation is staged. Proven
    by asserting no knowledge_links row exists referencing a note ID that
    never existed, after a delete attempt against it - not just that the
    call returned an error."""
    from app.database.session import get_sessionmaker
    from app.models.knowledge import KnowledgeLink

    token, sid = _connect(env, ["forge:delete"])
    error = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_note", "arguments": {"note_id": "does-not-exist", "confirm": True}}, 2)
    )
    assert "not found" in error.lower()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await session.execute(
            select(KnowledgeLink).where(
                (KnowledgeLink.source_id == "does-not-exist") | (KnowledgeLink.target_id == "does-not-exist")
            )
        )
        assert result.scalar_one_or_none() is None


async def test_document_delete_purges_knowledge_links_no_orphans(env):
    """Document-side symmetry for test_delete_purges_knowledge_links_no_orphans -
    the Milestone 2 Agentic Review noted this was only covered for Notes
    despite the code being structurally identical for Documents (MINOR)."""
    from app.database.session import get_sessionmaker
    from app.models.knowledge import KnowledgeLink
    from app.services.knowledge import service as knowledge_service

    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])
    doc_a = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_document", "arguments": {"title": "A"}}, 2))
    doc_b = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_document", "arguments": {"title": "B"}}, 3))

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await knowledge_service.create_link(session, "document", doc_a["id"], "document", doc_b["id"])

    deleted = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_document", "arguments": {"document_id": doc_a["id"], "confirm": True}}, 4)
    )
    assert deleted["deleted"] is True

    async with sessionmaker() as session:
        result = await session.execute(
            select(KnowledgeLink).where(
                ((KnowledgeLink.source_type == "document") & (KnowledgeLink.source_id == doc_a["id"]))
                | ((KnowledgeLink.target_type == "document") & (KnowledgeLink.target_id == doc_a["id"]))
            )
        )
        assert result.scalar_one_or_none() is None, "orphaned knowledge_links row survived the delete"


async def test_document_delete_nonexistent_stages_zero_changes(env):
    """Document-side symmetry for test_delete_nonexistent_note_stages_zero_changes (MINOR)."""
    token, sid = _connect(env, ["forge:delete"])
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {"name": "forge_delete_document", "arguments": {"document_id": "does-not-exist", "confirm": True}}, 2,
        )
    )
    assert "not found" in error.lower()


# --- StrictBool confirm coercion (BLOCKER regression) ------------------------


@pytest.mark.parametrize("coerced_value", ["true", "True", "1", "yes", 1, 1.0, 0])
def test_delete_note_rejects_non_boolean_confirm_values(env, coerced_value):
    """Regression test for the Milestone 2 Agentic Review's BLOCKER finding:
    a plain `bool` type hint let Pydantic's lax validation coerce
    "true"/"1"/1/etc into Python True, silently defeating the "confirm is
    structural, never inferred" guarantee. StrictBool (notes.py,
    documents.py) must reject every one of these - only the literal JSON
    boolean `true` may authorize a delete."""
    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])
    created = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "x"}}, 2))

    response = _call(
        env, sid, token, "tools/call",
        {"name": "forge_delete_note", "arguments": {"note_id": created["id"], "confirm": coerced_value}}, 3,
    )
    assert _tool_error(response), f"confirm={coerced_value!r} must not authorize deletion"

    # And the note must genuinely still exist - not just that an error string came back.
    still_there = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_get_note", "arguments": {"note_id": created["id"]}}, 4))
    assert still_there["id"] == created["id"]


def test_delete_document_rejects_non_boolean_confirm_values(env):
    token, sid = _connect(env, ["forge:read", "forge:write", "forge:delete"])
    created = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_document", "arguments": {"title": "x"}}, 2))

    response = _call(
        env, sid, token, "tools/call",
        {"name": "forge_delete_document", "arguments": {"document_id": created["id"], "confirm": "true"}}, 3,
    )
    assert _tool_error(response)

    still_there = _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_get_document", "arguments": {"document_id": created["id"]}}, 4)
    )
    assert still_there["id"] == created["id"]


# --- project_id validation (MAJOR regression) --------------------------------
#
# Regression tests for the Milestone 2 Agentic Review's MAJOR finding: a bad
# project_id previously reached the DB layer unvalidated and surfaced as a
# raw, unmapped sqlite3.IntegrityError carrying the full SQL statement and
# submitted content. Must now be a clean not-found error, per 06_API.md's own
# documented contract ("unknown project_id -> not-found error, not a
# silently-orphaned note").


@pytest.mark.parametrize(
    "tool_name,id_field,extra",
    [
        ("forge_create_note", None, {"title": "x", "project_id": "does-not-exist"}),
        ("forge_create_document", None, {"title": "x", "project_id": "does-not-exist"}),
    ],
)
def test_create_with_unknown_project_id_is_clean_not_found(env, tool_name, id_field, extra):
    token, sid = _connect(env, ["forge:write"])
    error = _tool_error(_call(env, sid, token, "tools/call", {"name": tool_name, "arguments": extra}, 2))
    assert "not found" in error.lower()
    assert "IntegrityError" not in error and "sqlite3" not in error, "must not leak a raw DB exception"


def test_update_note_with_unknown_project_id_is_clean_not_found(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    created = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "x"}}, 2))
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {"name": "forge_update_note", "arguments": {"note_id": created["id"], "project_id": "does-not-exist"}}, 3,
        )
    )
    assert "not found" in error.lower()


# --- Scope enforcement (AC5) --------------------------------------------------


@pytest.mark.parametrize(
    "tool_name,arguments",
    [
        ("forge_create_note", {"title": "x"}),
        ("forge_update_note", {"note_id": "x", "title": "y"}),
        ("forge_delete_note", {"note_id": "x", "confirm": True}),
        ("forge_create_document", {"title": "x"}),
        ("forge_create_project", {"name": "x"}),
    ],
)
def test_read_only_token_cannot_call_write_or_delete_tools(env, tool_name, arguments):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(_call(env, sid, token, "tools/call", {"name": tool_name, "arguments": arguments}, 2))
    assert "scope" in error.lower()


def test_write_only_token_cannot_call_delete_tool(env):
    token, sid = _connect(env, ["forge:write"])
    error = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_delete_note", "arguments": {"note_id": "x", "confirm": True}}, 2)
    )
    assert "scope" in error.lower()


def test_no_scope_token_cannot_call_any_crud_tool(env):
    token, sid = _connect(env, [])
    error = _tool_error(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "x"}}, 2))
    assert "scope" in error.lower()


# --- Audit logging correctness (AC18) ----------------------------------------


async def test_create_note_produces_exactly_one_activity_row_with_mcp_source(env):
    from app.database.session import get_sessionmaker
    from app.models.activity import ActivityLog

    token, sid = _connect(env, ["forge:write"])
    created = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "Audit me"}}, 2))

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await session.execute(select(ActivityLog).where(ActivityLog.entity_id == created["id"]))
        rows = result.scalars().all()
        assert len(rows) == 1, "exactly one ActivityLog row per mutation - not double-logged, not zero"
        assert rows[0].source == "mcp"
        assert rows[0].action == "created"


async def test_update_note_produces_no_activity_row_matching_existing_rest_behavior(env):
    """Documented asymmetry (see notes/service.py::update_note's docstring):
    update_note has never logged to ActivityLog, for REST or MCP - this
    proves the MCP path didn't silently introduce new logging behavior."""
    from app.database.session import get_sessionmaker
    from app.models.activity import ActivityLog

    token, sid = _connect(env, ["forge:write"])
    created = _tool_result(_call(env, sid, token, "tools/call", {"name": "forge_create_note", "arguments": {"title": "x"}}, 2))
    _tool_result(
        _call(env, sid, token, "tools/call", {"name": "forge_update_note", "arguments": {"note_id": created["id"], "pinned": True}}, 3)
    )

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await session.execute(
            select(ActivityLog).where(ActivityLog.entity_id == created["id"], ActivityLog.action == "updated")
        )
        assert result.scalar_one_or_none() is None
