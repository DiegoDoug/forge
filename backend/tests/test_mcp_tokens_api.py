from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(scope="module")
def client():
    # Same isolation pattern as test_projects_api.py - Settings/engine/
    # sessionmaker are process-wide lru_cache singletons, so this module
    # needs its own throwaway FORGE_DATA_DIR/env and cache-clear bracket.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    previous_bootstrap_token = os.environ.get("FORGE_MCP_BOOTSTRAP_TOKEN")
    previous_bootstrap_enabled = os.environ.get("FORGE_MCP_BOOTSTRAP_ENABLED")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-tokens-api-test-")
    os.environ["FORGE_MCP_BOOTSTRAP_TOKEN"] = "test-bootstrap-token"
    os.environ["FORGE_MCP_BOOTSTRAP_ENABLED"] = "true"

    from app.main import create_app

    app = create_app()
    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    if previous_data_dir is None:
        os.environ.pop("FORGE_DATA_DIR", None)
    else:
        os.environ["FORGE_DATA_DIR"] = previous_data_dir
    if previous_bootstrap_token is None:
        os.environ.pop("FORGE_MCP_BOOTSTRAP_TOKEN", None)
    else:
        os.environ["FORGE_MCP_BOOTSTRAP_TOKEN"] = previous_bootstrap_token
    if previous_bootstrap_enabled is None:
        os.environ.pop("FORGE_MCP_BOOTSTRAP_ENABLED", None)
    else:
        os.environ["FORGE_MCP_BOOTSTRAP_ENABLED"] = previous_bootstrap_enabled
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


BOOTSTRAP_HEADERS = {"Authorization": "Bearer test-bootstrap-token"}


def test_provisioning_requires_either_a_session_or_the_bootstrap_token(client):
    response = client.post("/api/mcp/tokens", json={"name": "x", "scopes": []})
    assert response.status_code == 401


def test_wrong_bootstrap_token_is_rejected(client):
    response = client.post(
        "/api/mcp/tokens", json={"name": "x", "scopes": []}, headers={"Authorization": "Bearer wrong-token"}
    )
    assert response.status_code == 401


def test_bootstrap_provisioning_works_before_first_run_setup_is_complete(client):
    # This client fixture never calls /api/setup - proves the headless
    # first-run scenario (01_SPEC.md SS4.3.1) works with no master password
    # configured yet, since the bootstrap path depends only on
    # FORGE_MASTER_KEY, never on config.master_password_hash.
    response = client.post(
        "/api/mcp/tokens", json={"name": "headless-provision", "scopes": ["forge:read"]}, headers=BOOTSTRAP_HEADERS
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "headless-provision"
    assert body["scopes"] == ["forge:read"]
    assert "token" in body and len(body["token"]) > 20
    assert "token_hash" not in body


def test_created_token_is_never_returned_again_on_list(client):
    create = client.post(
        "/api/mcp/tokens", json={"name": "list-me", "scopes": []}, headers=BOOTSTRAP_HEADERS
    ).json()

    listing = client.get("/api/mcp/tokens", headers=BOOTSTRAP_HEADERS)
    assert listing.status_code == 200
    entries = listing.json()
    match = next(e for e in entries if e["id"] == create["id"])
    assert "token" not in match
    assert "token_hash" not in match


def test_unknown_scope_is_rejected_by_validation(client):
    response = client.post(
        "/api/mcp/tokens", json={"name": "x", "scopes": ["not_a_real_scope"]}, headers=BOOTSTRAP_HEADERS
    )
    assert response.status_code == 422


def test_revoke_then_revoke_again_is_idempotent_not_an_error(client):
    create = client.post(
        "/api/mcp/tokens", json={"name": "revoke-me", "scopes": []}, headers=BOOTSTRAP_HEADERS
    ).json()

    first = client.delete(f"/api/mcp/tokens/{create['id']}", headers=BOOTSTRAP_HEADERS)
    second = client.delete(f"/api/mcp/tokens/{create['id']}", headers=BOOTSTRAP_HEADERS)
    assert first.status_code == 204
    assert second.status_code == 204

    listing = client.get("/api/mcp/tokens", headers=BOOTSTRAP_HEADERS).json()
    match = next(e for e in listing if e["id"] == create["id"])
    assert match["revoked_at"] is not None


def test_revoke_unknown_id_is_not_found(client):
    response = client.delete("/api/mcp/tokens/does-not-exist", headers=BOOTSTRAP_HEADERS)
    assert response.status_code == 404


def test_disabling_bootstrap_closes_provisioning_even_with_a_correct_token(client, monkeypatch):
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("FORGE_MCP_BOOTSTRAP_ENABLED", "false")
    get_settings.cache_clear()
    try:
        response = client.post(
            "/api/mcp/tokens", json={"name": "should-fail", "scopes": []}, headers=BOOTSTRAP_HEADERS
        )
        assert response.status_code == 401
    finally:
        monkeypatch.setenv("FORGE_MCP_BOOTSTRAP_ENABLED", "true")
        get_settings.cache_clear()


def test_browser_session_alone_can_provision_a_token_with_no_bootstrap_header():
    """Regression test for a BLOCKER found by the Milestone 1 Agentic Review:
    _require_session_or_bootstrap called require_auth(session) as a plain
    coroutine call rather than through FastAPI's dependency injection, so
    require_auth's Cookie()-marked parameter was never resolved from the
    actual request and always defaulted to None - meaning a valid
    forge_session cookie could never satisfy this dependency, silently
    forcing every call through the bootstrap-token path. This is exactly the
    scenario docs/Deployment.md's own hardening step creates (disable the
    bootstrap token after first provisioning) - without this fix, an
    operator who followed that advice would have had no way left to manage
    MCP tokens via the browser session.

    Uses its own fresh app (not the shared `client` fixture) since it needs
    to complete first-run setup, which would leak state into the other
    bootstrap-focused tests in this module if run against the shared client."""
    import os
    import tempfile

    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    previous_bootstrap_enabled = os.environ.get("FORGE_MCP_BOOTSTRAP_ENABLED")
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-mcp-cookie-auth-test-")
    # No FORGE_MCP_BOOTSTRAP_TOKEN set at all for this app instance - proves
    # the cookie path works entirely independently of bootstrap being
    # configured, not merely "also" works alongside it.
    os.environ.pop("FORGE_MCP_BOOTSTRAP_TOKEN", None)
    os.environ["FORGE_MCP_BOOTSTRAP_ENABLED"] = "true"

    try:
        from app.main import create_app
        from starlette.testclient import TestClient

        app = create_app()
        with TestClient(app) as c:
            setup = c.post("/api/setup", json={"master_password": "correct horse battery staple"})
            assert setup.status_code == 200
            assert "forge_session" in c.cookies

            # No Authorization header at all - only the session cookie, which
            # TestClient sends automatically now that it's set.
            response = c.post("/api/mcp/tokens", json={"name": "via-browser-session", "scopes": ["forge:read"]})
            assert response.status_code == 201
            assert response.json()["name"] == "via-browser-session"

            listing = c.get("/api/mcp/tokens")
            assert listing.status_code == 200
            assert any(t["name"] == "via-browser-session" for t in listing.json())
    finally:
        if previous_data_dir is None:
            os.environ.pop("FORGE_DATA_DIR", None)
        else:
            os.environ["FORGE_DATA_DIR"] = previous_data_dir
        if previous_bootstrap_enabled is None:
            os.environ.pop("FORGE_MCP_BOOTSTRAP_ENABLED", None)
        else:
            os.environ["FORGE_MCP_BOOTSTRAP_ENABLED"] = previous_bootstrap_enabled
        get_settings.cache_clear()
        get_engine.cache_clear()
        get_sessionmaker.cache_clear()
