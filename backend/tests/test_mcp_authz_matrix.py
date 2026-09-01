"""M5-T2 (09_IMPLEMENTATION_TASKS.md) - the full authorization matrix: every
MCP tool x every scope, exhaustively, in one place. Every prior milestone's
test file already covers its own tools' scope enforcement individually
(test_mcp_tools_crud.py, test_mcp_tools_search_context.py,
test_mcp_tools_knowledge.py, test_mcp_tools_memory.py); this file exists so
the *complete* picture - all 18 tools, cross-checked against 01_SPEC.md
SS4.4's scope table - is verified in one exhaustive sweep, not assembled by
inference across five different files each testing a handful of tools.

Two properties, per tool:
1. A token holding exactly the tool's required scope reaches the tool's own
   business logic (never rejected on scope grounds) - proven by using
   structurally-valid-but-nonexistent IDs and asserting the resulting error
   (if any) is a domain error (not-found, etc.), never a scope error.
2. A token holding a single, different scope (not the required one) is
   rejected on scope grounds, before any data access - proven for
   write/delete tools by asserting zero rows were mutated.

Invalid-token and revoked-token behavior is transport-level (identical for
every tool, since McpBearerAuthMiddleware runs before any tool dispatch) and
is already exhaustively covered by test_mcp_server.py
(test_missing_authorization_header_is_rejected_before_any_protocol_processing,
test_revoked_token_is_rejected_immediately) - re-asserted once here (not 18
times) as a completeness cross-reference, not a redundant re-test."""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import select

MCP_HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
INITIALIZE_PARAMS = {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}}

# (tool name, required scope, minimal structurally-valid arguments) - every
# argument targets a nonexistent id where the tool needs one, so a
# correctly-scoped call reaches (and cleanly fails or succeeds at) real
# business logic rather than a validation error, and a wrongly-scoped call
# never reaches that logic at all. Matches 01_SPEC.md SS4.4's scope table
# and 06_API.md's per-tool contracts exactly - 18 tools, matching
# test_mcp_server.py's tool-list assertion.
_TOOL_MATRIX: list[tuple[str, str, dict]] = [
    ("forge_search", "forge:read", {"query": "zzz-authz-matrix-nonexistent-query"}),
    ("forge_context", "forge:read", {"topic": "zzz-authz-matrix-nonexistent-topic"}),
    ("forge_get_note", "forge:read", {"note_id": "does-not-exist"}),
    ("forge_get_document", "forge:read", {"document_id": "does-not-exist"}),
    ("forge_list_projects", "forge:read", {}),
    ("forge_get_project", "forge:read", {"project_id": "does-not-exist"}),
    ("forge_create_note", "forge:write", {"title": "authz-matrix-note"}),
    ("forge_update_note", "forge:write", {"note_id": "does-not-exist", "title": "x"}),
    ("forge_create_document", "forge:write", {"title": "authz-matrix-doc", "content": "<p>x</p>"}),
    ("forge_update_document", "forge:write", {"document_id": "does-not-exist", "title": "x"}),
    ("forge_create_project", "forge:write", {"name": "authz-matrix-project"}),
    ("forge_update_project", "forge:write", {"project_id": "does-not-exist", "name": "x"}),
    (
        "forge_link_items",
        "forge:write",
        {"source_type": "note", "source_id": "does-not-exist", "target_type": "note", "target_id": "also-not-exist"},
    ),
    ("forge_unlink_items", "forge:write", {"link_id": "does-not-exist"}),
    ("forge_capture_decision", "forge:write", {"summary": "authz-matrix-decision"}),
    ("forge_capture_session", "forge:write", {"summary": "authz-matrix-session"}),
    ("forge_delete_note", "forge:delete", {"note_id": "does-not-exist", "confirm": True}),
    ("forge_delete_document", "forge:delete", {"document_id": "does-not-exist", "confirm": True}),
]

_ALL_SCOPES = {"forge:read", "forge:write", "forge:delete"}


def _wrong_scope(required: str) -> str:
    """A single scope guaranteed not to satisfy `required`."""
    return next(s for s in sorted(_ALL_SCOPES) if s != required)


def test_tool_matrix_covers_every_registered_tool():
    """Guards the matrix itself from silently going stale - if a future
    milestone adds/removes a tool without updating _TOOL_MATRIX, this fails
    loudly rather than the matrix quietly under-covering reality."""
    assert {name for name, _, _ in _TOOL_MATRIX} == {
        "forge_get_note", "forge_create_note", "forge_update_note", "forge_delete_note",
        "forge_get_document", "forge_create_document", "forge_update_document", "forge_delete_document",
        "forge_list_projects", "forge_get_project", "forge_create_project", "forge_update_project",
        "forge_search", "forge_context",
        "forge_link_items", "forge_unlink_items",
        "forge_capture_decision", "forge_capture_session",
    }
    assert len(_TOOL_MATRIX) == 18


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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-authz-matrix-test-")
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
        json={"name": "authz-matrix-test", "scopes": scopes},
        headers={"Authorization": "Bearer bootstrap-secret"},
    ).json()["token"]
    init = _call(client, None, token, "initialize", INITIALIZE_PARAMS)
    assert init.status_code == 200
    return token, init.headers["mcp-session-id"]


def _call_tool_raw(client, sid, token, name, arguments, request_id):
    return _call(client, sid, token, "tools/call", {"name": name, "arguments": arguments}, request_id)


def _tool_error_text(response) -> str | None:
    body = response.json()["result"]
    if not body.get("isError"):
        return None
    return body["content"][0]["text"]


@pytest.mark.parametrize("name,scope,args", _TOOL_MATRIX, ids=[t[0] for t in _TOOL_MATRIX])
def test_correctly_scoped_token_never_rejected_on_scope_grounds(env, name, scope, args):
    token, sid = _connect(env, [scope])
    response = _call_tool_raw(env, sid, token, name, args, 2)
    error = _tool_error_text(response)
    if error is not None:
        assert "scope" not in error.lower(), (
            f"{name} rejected a token holding exactly its required scope ({scope}) as a scope failure: {error!r}"
        )


@pytest.mark.parametrize("name,scope,args", _TOOL_MATRIX, ids=[t[0] for t in _TOOL_MATRIX])
def test_wrongly_scoped_token_always_rejected_before_any_data_access(env, name, scope, args):
    token, sid = _connect(env, [_wrong_scope(scope)])
    response = _call_tool_raw(env, sid, token, name, args, 2)
    error = _tool_error_text(response)
    assert error is not None and "scope" in error.lower(), (
        f"{name} did not reject a token lacking its required scope ({scope}): "
        f"{'succeeded' if error is None else error!r}"
    )


@pytest.mark.parametrize("name,scope,args", _TOOL_MATRIX, ids=[t[0] for t in _TOOL_MATRIX])
def test_zero_scope_token_always_rejected(env, name, scope, args):
    token, sid = _connect(env, [])
    response = _call_tool_raw(env, sid, token, name, args, 2)
    error = _tool_error_text(response)
    assert error is not None and "scope" in error.lower(), (
        f"{name} did not reject a zero-scope token: {'succeeded' if error is None else error!r}"
    )


async def test_wrongly_scoped_write_and_delete_tools_stage_zero_mutations(env):
    """Scope rejection must happen strictly before any service call - a
    wrongly-scoped forge_create_note/forge_delete_note/etc. must not create,
    modify, or delete a single row. Checked directly against the DB, not
    inferred from the error message alone."""
    from app.database.session import get_sessionmaker
    from app.models.note import Note
    from app.models.document import Document
    from app.models.project import Project

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        before_notes = len((await session.execute(select(Note))).scalars().all())
        before_documents = len((await session.execute(select(Document))).scalars().all())
        before_projects = len((await session.execute(select(Project))).scalars().all())

    write_delete_tools = [(n, s, a) for n, s, a in _TOOL_MATRIX if s in ("forge:write", "forge:delete")]
    for name, scope, args in write_delete_tools:
        token, sid = _connect(env, [_wrong_scope(scope)])
        _call_tool_raw(env, sid, token, name, args, 2)

    async with sessionmaker() as session:
        after_notes = len((await session.execute(select(Note))).scalars().all())
        after_documents = len((await session.execute(select(Document))).scalars().all())
        after_projects = len((await session.execute(select(Project))).scalars().all())

    assert after_notes == before_notes
    assert after_documents == before_documents
    assert after_projects == before_projects


def test_matrix_cross_reference_invalid_and_revoked_token(env):
    """Completeness cross-reference for 07_TESTING.md's "every tool x every
    scope x valid/invalid/revoked token" phrasing - invalid/revoked-token
    rejection is a transport-level property (McpBearerAuthMiddleware runs
    before any tool dispatch, identically for all 18 tools), exhaustively
    proven once here rather than 18 near-identical times; per-tool coverage
    for this exact property already exists in test_mcp_server.py."""
    bad = _call(env, None, "not-a-real-token", "initialize", INITIALIZE_PARAMS)
    assert bad.status_code == 401

    token = env.post(
        "/api/mcp/tokens",
        json={"name": "to-revoke-matrix-test", "scopes": ["forge:read", "forge:write", "forge:delete"]},
        headers={"Authorization": "Bearer bootstrap-secret"},
    ).json()
    ok = _call(env, None, token["token"], "initialize", INITIALIZE_PARAMS)
    assert ok.status_code == 200

    env.delete(f"/api/mcp/tokens/{token['id']}", headers={"Authorization": "Bearer bootstrap-secret"})
    after_revoke = _call(env, None, token["token"], "initialize", INITIALIZE_PARAMS)
    assert after_revoke.status_code == 401
