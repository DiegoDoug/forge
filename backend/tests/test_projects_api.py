from __future__ import annotations

import os
import tempfile

import pytest

from app.services.model_playground.providers import PROVIDER_REGISTRY
from app.services.model_playground.providers.base import AdapterResult


class _FakeAdapter:
    def __init__(self, *, text="hello", error=None):
        self.text = text
        self.error = error

    async def complete(self, *, api_key, model, prompt, base_url=None) -> AdapterResult:
        if self.error is not None:
            raise self.error
        return AdapterResult(response_text=self.text, prompt_tokens=3, completion_tokens=7)


@pytest.fixture(autouse=True)
def _restore_adapters():
    originals = {key: spec.adapter for key, spec in PROVIDER_REGISTRY.items()}
    yield
    for key, adapter in originals.items():
        object.__setattr__(PROVIDER_REGISTRY[key], "adapter", adapter)


def _install_fake_adapter(provider: str, adapter: _FakeAdapter) -> None:
    object.__setattr__(PROVIDER_REGISTRY[provider], "adapter", adapter)


@pytest.fixture(scope="module")
def client():
    # Same isolation pattern as test_model_playground_api.py - Settings/engine/
    # sessionmaker are process-wide lru_cache singletons, so this module needs
    # its own throwaway FORGE_DATA_DIR and cache-clear bracket.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-projects-test-")

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


def test_project_routes_require_a_session(client):
    assert client.get("/api/projects").status_code == 401
    assert client.post("/api/projects", json={"name": "x"}).status_code == 401
    assert client.get("/api/projects/does-not-exist").status_code == 401
    assert client.patch("/api/projects/does-not-exist", json={}).status_code == 401
    assert client.delete("/api/projects/does-not-exist").status_code == 401
    assert client.post("/api/projects/does-not-exist/ai/run", json={"prompt": "hi"}).status_code == 401


def test_create_requires_a_name(authed_client):
    response = authed_client.post("/api/projects", json={"name": ""})
    assert response.status_code == 422


def test_full_crud_happy_path(authed_client):
    create = authed_client.post("/api/projects", json={"name": "Client A", "description": "test"})
    assert create.status_code == 201
    project = create.json()
    assert project["name"] == "Client A"
    assert project["secret_count"] == 0

    get_resp = authed_client.get(f"/api/projects/{project['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == project["id"]

    listed = authed_client.get("/api/projects")
    assert any(p["id"] == project["id"] for p in listed.json())

    updated = authed_client.patch(f"/api/projects/{project['id']}", json={"name": "Client A Renamed"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Client A Renamed"

    deleted = authed_client.delete(f"/api/projects/{project['id']}")
    assert deleted.status_code == 204

    assert authed_client.get(f"/api/projects/{project['id']}").status_code == 404


def test_get_update_delete_unknown_project_returns_404(authed_client):
    assert authed_client.get("/api/projects/does-not-exist").status_code == 404
    assert authed_client.patch("/api/projects/does-not-exist", json={"name": "x"}).status_code == 404
    assert authed_client.delete("/api/projects/does-not-exist").status_code == 404


def test_invalid_default_provider_model_combinations_return_422(authed_client):
    unknown_provider = authed_client.post(
        "/api/projects", json={"name": "P", "default_provider": "made-up", "default_model": "x"}
    )
    assert unknown_provider.status_code == 422

    model_not_in_catalogue = authed_client.post(
        "/api/projects", json={"name": "P", "default_provider": "openai", "default_model": "not-a-real-model"}
    )
    assert model_not_in_catalogue.status_code == 422

    only_provider_set = authed_client.post("/api/projects", json={"name": "P", "default_provider": "openai"})
    assert only_provider_set.status_code == 422


def test_ai_run_without_default_configured_returns_400(authed_client):
    project = authed_client.post("/api/projects", json={"name": "No AI"}).json()

    response = authed_client.post(f"/api/projects/{project['id']}/ai/run", json={"prompt": "hi"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "project_ai_not_configured"


def test_ai_run_with_configured_default_but_no_credential_returns_400(authed_client):
    project = authed_client.post(
        "/api/projects", json={"name": "Needs Credential", "default_provider": "anthropic", "default_model": "claude-sonnet-5"}
    ).json()

    response = authed_client.post(f"/api/projects/{project['id']}/ai/run", json={"prompt": "hi"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "provider_not_configured"


def test_ai_run_success_appears_in_project_and_playground_history(authed_client):
    _install_fake_adapter("openai", _FakeAdapter(text="hello from project"))
    authed_client.post("/api/model-playground/credentials", json={"provider": "openai", "api_key": "sk-test"})
    project = authed_client.post(
        "/api/projects", json={"name": "AI Ready", "default_provider": "openai", "default_model": "gpt-4.1"}
    ).json()

    run_response = authed_client.post(f"/api/projects/{project['id']}/ai/run", json={"prompt": "hello world"})
    assert run_response.status_code == 201
    run = run_response.json()
    assert run["results"][0]["status"] == "success"
    assert run["results"][0]["response_text"] == "hello from project"

    project_runs = authed_client.get(f"/api/projects/{project['id']}/ai/runs")
    assert [item["id"] for item in project_runs.json()["items"]] == [run["id"]]

    playground_runs = authed_client.get("/api/model-playground/runs")
    assert any(item["id"] == run["id"] for item in playground_runs.json()["items"])


def test_delete_project_unscopes_secret_note_document_without_deleting_them(authed_client):
    project = authed_client.post("/api/projects", json={"name": "To Delete"}).json()
    pid = project["id"]

    secret = authed_client.post(
        "/api/secrets/secrets", json={"name": "s1", "value": "shh", "project_id": pid}
    ).json()
    note = authed_client.post("/api/notes", json={"title": "n1", "project_id": pid}).json()
    document = authed_client.post("/api/documents", json={"title": "d1", "project_id": pid}).json()

    detail = authed_client.get(f"/api/projects/{pid}")
    assert detail.json()["secret_count"] == 1
    assert detail.json()["note_count"] == 1
    assert detail.json()["document_count"] == 1

    assert authed_client.delete(f"/api/projects/{pid}").status_code == 204

    reloaded_secret = authed_client.get(f"/api/secrets/secrets/{secret['id']}").json()
    reloaded_document = authed_client.get(f"/api/documents/{document['id']}").json()

    assert reloaded_secret["project_id"] is None
    assert reloaded_secret["name"] == "s1"
    assert reloaded_document["project_id"] is None
    assert reloaded_document["title"] == "d1"
    assert any(n["id"] == note["id"] and n["project_id"] is None for n in authed_client.get("/api/notes").json())


def test_secrets_notes_documents_list_filter_by_project_id(authed_client):
    project_a = authed_client.post("/api/projects", json={"name": "Filter A"}).json()
    project_b = authed_client.post("/api/projects", json={"name": "Filter B"}).json()

    authed_client.post("/api/secrets/secrets", json={"name": "a-secret", "value": "v", "project_id": project_a["id"]})
    authed_client.post("/api/secrets/secrets", json={"name": "b-secret", "value": "v", "project_id": project_b["id"]})
    authed_client.post("/api/notes", json={"title": "a-note", "project_id": project_a["id"]})
    authed_client.post("/api/documents", json={"title": "a-doc", "project_id": project_a["id"]})

    secrets_a = authed_client.get("/api/secrets/secrets", params={"project_id": project_a["id"]}).json()
    assert {s["name"] for s in secrets_a} == {"a-secret"}

    notes_a = authed_client.get("/api/notes", params={"project_id": project_a["id"]}).json()
    assert {n["title"] for n in notes_a} == {"a-note"}

    documents_a = authed_client.get("/api/documents", params={"project_id": project_a["id"]}).json()
    assert {d["title"] for d in documents_a} == {"a-doc"}
