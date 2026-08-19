"""End-to-end MCP tests for forge://projects, forge://projects/{project_id}
(Milestone 4, 06_API.md SS5). Same real-JSON-RPC-through-the-mounted-app
pattern as the tool test files."""

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
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-resources-test-")
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


def _call_tool(client, sid, token, name, arguments, request_id):
    return _tool_result(_call(client, sid, token, "tools/call", {"name": name, "arguments": arguments}, request_id))


def _read_resource(client, sid, token, uri, request_id):
    response = _call(client, sid, token, "resources/read", {"uri": uri}, request_id)
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    return json.loads(result["contents"][0]["text"])


def _read_resource_error(client, sid, token, uri, request_id):
    response = _call(client, sid, token, "resources/read", {"uri": uri}, request_id)
    body = response.json()
    return body


def test_forge_projects_resource_lists_non_archived_projects_with_counts(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    project = _call_tool(env, sid, token, "forge_create_project", {"name": "Resource Test Project"}, 2)

    projects = _read_resource(env, sid, token, "forge://projects", 3)
    assert any(p["id"] == project["id"] and p["name"] == "Resource Test Project" for p in projects)
    match = next(p for p in projects if p["id"] == project["id"])
    assert "secret_count" not in match
    assert match["note_count"] == 0 and match["document_count"] == 0


def test_forge_projects_resource_excludes_archived_projects(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    project = _call_tool(env, sid, token, "forge_create_project", {"name": "Will Be Archived"}, 2)
    _call_tool(env, sid, token, "forge_update_project", {"project_id": project["id"], "archived": True}, 3)

    projects = _read_resource(env, sid, token, "forge://projects", 4)
    assert not any(p["id"] == project["id"] for p in projects)


def test_forge_project_resource_returns_one_project_detail(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    project = _call_tool(env, sid, token, "forge_create_project", {"name": "Detail Resource Project"}, 2)

    detail = _read_resource(env, sid, token, f"forge://projects/{project['id']}", 3)
    assert detail["id"] == project["id"]
    assert detail["name"] == "Detail Resource Project"


def test_forge_project_resource_unknown_id_errors(env):
    token, sid = _connect(env, ["forge:read", "forge:write"])
    body = _read_resource_error(env, sid, token, "forge://projects/does-not-exist", 2)
    assert "error" in body


def test_forge_project_resource_requires_forge_read_scope(env):
    """The template resource - unlike forge://projects (see
    app/mcp/resources.py's module docstring for why the static resource
    cannot enforce this the same way) - genuinely enforces forge:read,
    exactly like forge_get_project the tool does."""
    token, sid = _connect(env, ["forge:write"])
    project = _call_tool(env, sid, token, "forge_create_project", {"name": "Scope Check Project"}, 2)

    body = _read_resource_error(env, sid, token, f"forge://projects/{project['id']}", 3)
    assert "error" in body


def test_forge_projects_resource_appears_in_resources_list_for_auto_discovery(env):
    """06_API.md SS5's explicit requirement: forge://projects must be
    discoverable via resources/list (not only resources/templates/list),
    since it has no URI variable."""
    token, sid = _connect(env, ["forge:read"])
    response = _call(env, sid, token, "resources/list", {}, 2)
    uris = {r["uri"] for r in response.json()["result"]["resources"]}
    assert "forge://projects" in uris
