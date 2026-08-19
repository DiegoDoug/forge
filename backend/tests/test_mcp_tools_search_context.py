"""End-to-end MCP tests for forge_search/forge_context (Milestone 3).
Same real-JSON-RPC-through-the-mounted-app pattern as
test_mcp_tools_crud.py - exercises real FTS5 (via the real Alembic
migration chain create_app() runs), not an in-memory schema without the
notes_fts/documents_fts virtual tables."""

from __future__ import annotations

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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-search-test-")
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
    """See test_mcp_tools_crud.py::_tool_result's docstring for why both
    structuredContent shapes and the content[0].text fallback are handled -
    same MCP SDK serialization quirk, unrelated to this phase's own code."""
    body = response.json()["result"]
    assert not body.get("isError"), body
    structured = body.get("structuredContent")
    if structured is not None:
        if set(structured.keys()) == {"result"}:
            return structured["result"]
        return structured
    import json

    return json.loads(body["content"][0]["text"])


def _tool_error(response) -> str:
    body = response.json()["result"]
    assert body.get("isError"), body
    return body["content"][0]["text"]


def _call_tool(client, sid, token, name, arguments, request_id):
    return _tool_result(_call(client, sid, token, "tools/call", {"name": name, "arguments": arguments}, request_id))


# --- forge_search -------------------------------------------------------


def test_forge_search_finds_notes_and_documents(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    _call_tool(env, sid, token, "forge_create_note", {"title": "Alpha", "content": "a unique-zephyr note"}, 2)
    _call_tool(env, sid, token, "forge_create_document", {"title": "Beta", "content": "<p>a unique-zephyr document</p>"}, 3)

    results = _call_tool(env, sid, token, "forge_search", {"query": "unique-zephyr"}, 4)
    types = {r["type"] for r in results}
    assert types == {"note", "document"}
    for r in results:
        assert set(r.keys()) == {"id", "type", "title", "snippet", "project_id", "updated_at"}


def test_forge_search_types_filter(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    _call_tool(env, sid, token, "forge_create_note", {"title": "OnlyNote", "content": "unique-quokka term"}, 2)

    note_only = _call_tool(env, sid, token, "forge_search", {"query": "unique-quokka", "types": ["note"]}, 3)
    assert all(r["type"] == "note" for r in note_only)

    doc_only = _call_tool(env, sid, token, "forge_search", {"query": "unique-quokka", "types": ["document"]}, 4)
    assert doc_only == []


def test_forge_search_rejects_empty_query(env):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(_call(env, sid, token, "tools/call", {"name": "forge_search", "arguments": {"query": "  "}}, 2))
    assert "query" in error.lower()


def test_forge_search_rejects_query_over_200_chars(env):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(
        _call(env, sid, token, "tools/call", {"name": "forge_search", "arguments": {"query": "x" * 201}}, 2)
    )
    assert "query" in error.lower()


def test_forge_search_never_returns_secret_data(env):
    """AC12 - forge_search must never surface Secret names/metadata, unlike
    search_service.global_search (which this tool deliberately does not
    call). Adversarial: a Secret whose name matches the query term must not
    leak into the output even though a plaintext-search-everything
    implementation would have found it."""
    token, sid = _connect(env, ["forge:read", "forge:write"])
    _call_tool(env, sid, token, "forge_create_note", {"title": "unrelated", "content": "unique-narwhal note"}, 2)

    results = _call_tool(env, sid, token, "forge_search", {"query": "unique-narwhal"}, 3)
    for r in results:
        assert r["type"] in ("note", "document")
        assert "secret" not in r


def test_forge_search_invalid_project_id_errors(env):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {"name": "forge_search", "arguments": {"query": "anything", "project_id": "does-not-exist"}}, 2,
        )
    )
    assert "not found" in error.lower()


def test_forge_search_project_scoping_is_query_level_not_post_filtered(env):
    """AC13a - a project-scoped forge_search must apply project_id inside
    the FTS query itself, before the 50-per-type cap, not filter an
    unscoped top-50 afterward. Deterministic proof: project B gets 60 notes
    engineered to rank far higher (5x term repetition) than project A's 30
    notes (single term occurrence). An unscoped-then-filtered
    implementation's top-50-by-rank would be entirely consumed by B's
    higher-relevance rows, leaving 0 of A's notes after filtering. The
    correct, query-scoped implementation returns all 30 of A's matches
    regardless of B's presence."""
    token, sid = _connect(env, ["forge:read", "forge:write"])
    project_a = _call_tool(env, sid, token, "forge_create_project", {"name": "Project A (AC13a)"}, 2)["id"]
    project_b = _call_tool(env, sid, token, "forge_create_project", {"name": "Project B (AC13a)"}, 3)["id"]

    request_id = 4
    for i in range(60):
        _call_tool(
            env, sid, token, "forge_create_note",
            {"title": f"B{i}", "content": "quixotic " * 5, "project_id": project_b}, request_id,
        )
        request_id += 1
    for i in range(30):
        _call_tool(
            env, sid, token, "forge_create_note",
            {"title": f"A{i}", "content": "quixotic", "project_id": project_a}, request_id,
        )
        request_id += 1

    scoped = _call_tool(
        env, sid, token, "forge_search",
        {"query": "quixotic", "types": ["note"], "project_id": project_a}, request_id,
    )
    assert len(scoped) == 30, "project-scoped search must return every one of project A's matches, unaffected by project B's higher-ranked notes"
    assert all(r["project_id"] == project_a for r in scoped)


# --- forge_context --------------------------------------------------------


async def test_forge_context_aggregates_project_notes_documents_tags_links(env):
    """AC11 - every field forge_context returns is backed by an existing
    Forge query; this test proves the aggregate shape end to end,
    including tags (a coverage gap flagged by the Milestone 3 Agentic
    Review, MINOR: the original version of this test never actually
    exercised the tags field despite its name and despite AC11 requiring
    it)."""
    from app.database.session import get_sessionmaker
    from app.services.knowledge import service as knowledge_service

    token, sid = _connect(env, ["forge:read", "forge:write"])
    project_id = _call_tool(env, sid, token, "forge_create_project", {"name": "Context Project"}, 2)["id"]
    note = _call_tool(
        env, sid, token, "forge_create_note",
        {"title": "Context note", "content": "unique-griffin content", "project_id": project_id}, 3,
    )
    document = _call_tool(
        env, sid, token, "forge_create_document",
        {"title": "Context doc", "content": "<p>unique-griffin content</p>", "project_id": project_id}, 4,
    )
    _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": note["id"], "target_type": "document", "target_id": document["id"]}, 5,
    )

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await knowledge_service.add_tag(session, "note", note["id"], tag_id=None, name="griffin-tag", color="#123456")

    context = _call_tool(env, sid, token, "forge_context", {"topic": "unique-griffin", "project_id": project_id}, 6)
    assert context["project"]["id"] == project_id
    assert "secret_count" not in context["project"]
    assert [n["id"] for n in context["notes"]] == [note["id"]]
    assert [d["id"] for d in context["documents"]] == [document["id"]]
    assert [t["name"] for t in context["notes"][0]["tags"]] == ["griffin-tag"]
    assert context["documents"][0]["tags"] == [], "the document was never tagged - must not inherit the note's tag"
    assert context["links"] == [
        {"source_type": "note", "source_id": note["id"], "target_type": "document", "target_id": document["id"]}
    ]


async def test_forge_context_excludes_links_to_items_outside_the_matched_set(env):
    """Milestone 3 Agentic Review MAJOR finding: forge_context's links
    field must only include edges BETWEEN matched items (01_SPEC.md SS5.2's
    literal wording), not any link touching a matched item regardless of
    whether the other side appears anywhere else in the response. A link to
    an unmatched item would otherwise be a dangling reference with no
    accompanying title/content in the same payload."""
    token, sid = _connect(env, ["forge:read", "forge:write"])
    matched = _call_tool(env, sid, token, "forge_create_note", {"title": "Matched", "content": "unique-okapi content"}, 2)
    unmatched = _call_tool(env, sid, token, "forge_create_note", {"title": "Unmatched", "content": "completely unrelated"}, 3)
    _call_tool(
        env, sid, token, "forge_link_items",
        {"source_type": "note", "source_id": matched["id"], "target_type": "note", "target_id": unmatched["id"]}, 4,
    )

    context = _call_tool(env, sid, token, "forge_context", {"topic": "unique-okapi"}, 5)
    assert [n["id"] for n in context["notes"]] == [matched["id"]]
    assert context["links"] == [], "a link to an item outside the matched set must not appear"


def test_forge_context_null_project_when_omitted(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    context = _call_tool(env, sid, token, "forge_context", {"topic": "anything-not-matching-xyz"}, 2)
    assert context["project"] is None


def test_forge_context_invalid_project_id_errors_not_silently_unfiltered(env):
    """AC13 - an invalid project_id must produce an explicit error, not
    silently-unfiltered (or silently empty) results."""
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(
        _call(
            env, sid, token, "tools/call",
            {"name": "forge_context", "arguments": {"topic": "anything", "project_id": "does-not-exist"}}, 2,
        )
    )
    assert "not found" in error.lower()


def test_forge_context_rejects_empty_topic(env):
    token, sid = _connect(env, ["forge:read"])
    error = _tool_error(_call(env, sid, token, "tools/call", {"name": "forge_context", "arguments": {"topic": "  "}}, 2))
    assert "topic" in error.lower()


# --- scope enforcement ------------------------------------------------------


def test_forge_search_and_context_require_forge_read(env):
    token, sid = _connect(env, [])
    for name, arguments in (("forge_search", {"query": "x"}), ("forge_context", {"topic": "x"})):
        error = _tool_error(_call(env, sid, token, "tools/call", {"name": name, "arguments": arguments}, 2))
        assert "scope" in error.lower()
