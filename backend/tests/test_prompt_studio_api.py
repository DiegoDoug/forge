from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(scope="module")
def client():
    # Same isolation pattern as test_project_init_api.py - Settings/engine/
    # sessionmaker are process-wide lru_cache singletons, so this module needs
    # its own throwaway FORGE_DATA_DIR and cache-clear bracket.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-prompt-studio-test-")

    from app.main import create_app

    app = create_app()
    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    if previous_data_dir is None:
        os.environ.pop("FORGE_DATA_DIR", None)
    else:
        os.environ["FORGE_DATA_DIR"] = previous_data_dir
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


@pytest.fixture(scope="module")
def authed_client(client):
    setup_response = client.post("/api/setup", json={"master_password": "correct horse battery staple"})
    assert setup_response.status_code == 200
    return client


VAR = {"name": "audience", "type": "string", "required": True}


def _create_payload(name="Summary", body="Write for ${audience}.", variables=None, tags=None):
    return {"name": name, "body": body, "variables": variables if variables is not None else [VAR], "tags": tags or []}


def test_list_prompts_requires_a_session(client):
    response = client.get("/api/prompts")
    assert response.status_code == 401


def test_create_then_get_prompt(authed_client):
    create_response = authed_client.post("/api/prompts", json=_create_payload())
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["version_number"] == 1
    assert body["variables"][0]["name"] == "audience"

    get_response = authed_client.get(f"/api/prompts/{body['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Summary"


def test_create_missing_name_returns_422(authed_client):
    payload = _create_payload()
    del payload["name"]
    response = authed_client.post("/api/prompts", json=payload)
    assert response.status_code == 422


def test_create_undeclared_placeholder_returns_422(authed_client):
    payload = _create_payload(body="Write for ${typo}.", variables=[VAR])
    response = authed_client.post("/api/prompts", json=payload)
    assert response.status_code == 422


def test_get_missing_prompt_returns_404(authed_client):
    response = authed_client.get("/api/prompts/does-not-exist")
    assert response.status_code == 404


def test_update_metadata_does_not_bump_version(authed_client):
    created = authed_client.post("/api/prompts", json=_create_payload(name="Original")).json()

    response = authed_client.patch(f"/api/prompts/{created['id']}", json={"name": "Renamed"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Renamed"
    assert body["version_number"] == 1


def test_update_content_bumps_version_and_appears_in_history(authed_client):
    created = authed_client.post("/api/prompts", json=_create_payload()).json()

    response = authed_client.put(
        f"/api/prompts/{created['id']}/content",
        json={"body": "New body for ${audience}.", "variables": [VAR]},
    )
    assert response.status_code == 200
    assert response.json()["version_number"] == 2

    versions_response = authed_client.get(f"/api/prompts/{created['id']}/versions")
    assert versions_response.status_code == 200
    items = versions_response.json()["items"]
    assert len(items) == 2
    assert [v["version_number"] for v in items] == [2, 1]


def test_update_content_with_undeclared_placeholder_creates_no_new_version(authed_client):
    created = authed_client.post("/api/prompts", json=_create_payload()).json()

    response = authed_client.put(
        f"/api/prompts/{created['id']}/content",
        json={"body": "Write for ${typo}.", "variables": [VAR]},
    )
    assert response.status_code == 422

    versions_response = authed_client.get(f"/api/prompts/{created['id']}/versions")
    assert len(versions_response.json()["items"]) == 1  # still just the initial version


def test_full_lifecycle_create_edit_edit_restore_duplicate_delete(authed_client):
    created = authed_client.post(
        "/api/prompts", json=_create_payload(name="Lifecycle", body="v1 ${audience}")
    ).json()
    prompt_id = created["id"]

    authed_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "v2 ${audience}", "variables": [VAR]})
    authed_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "v3 ${audience}", "variables": [VAR]})

    versions = authed_client.get(f"/api/prompts/{prompt_id}/versions").json()["items"]
    assert len(versions) == 3
    v1_id = next(v["id"] for v in versions if v["version_number"] == 1)

    restore_response = authed_client.post(f"/api/prompts/{prompt_id}/versions/{v1_id}/restore")
    assert restore_response.status_code == 200
    restored = restore_response.json()
    assert restored["version_number"] == 4
    assert restored["body"] == "v1 ${audience}"
    detail = authed_client.get(f"/api/prompts/{prompt_id}").json()
    assert detail["version_number"] == 4
    assert detail["body"] == "v1 ${audience}"

    duplicate_response = authed_client.post(f"/api/prompts/{prompt_id}/duplicate")
    assert duplicate_response.status_code == 201
    duplicate = duplicate_response.json()
    assert duplicate["id"] != prompt_id
    assert duplicate["version_number"] == 1

    delete_response = authed_client.delete(f"/api/prompts/{prompt_id}")
    assert delete_response.status_code == 204
    assert authed_client.get(f"/api/prompts/{prompt_id}").status_code == 404

    # the duplicate is untouched by deleting the original
    assert authed_client.get(f"/api/prompts/{duplicate['id']}").status_code == 200


def test_get_version_from_wrong_prompt_returns_404(authed_client):
    prompt_a = authed_client.post("/api/prompts", json=_create_payload(name="A")).json()
    prompt_b = authed_client.post("/api/prompts", json=_create_payload(name="B")).json()
    versions_a = authed_client.get(f"/api/prompts/{prompt_a['id']}/versions").json()["items"]

    response = authed_client.get(f"/api/prompts/{prompt_b['id']}/versions/{versions_a[0]['id']}")
    assert response.status_code == 404


def test_search_and_tag_filter(authed_client):
    authed_client.post("/api/prompts", json=_create_payload(name="Searchable Unique Name", tags=["findme"]))

    search_response = authed_client.get("/api/prompts", params={"search": "Searchable Unique"})
    assert any(p["name"] == "Searchable Unique Name" for p in search_response.json()["items"])

    tag_response = authed_client.get("/api/prompts", params={"tag": "findme"})
    assert any("findme" in p["tags"] for p in tag_response.json()["items"])
