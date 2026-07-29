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

    async def complete(self, *, api_key: str, model: str, prompt: str) -> AdapterResult:
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
    # Same isolation pattern as test_prompt_studio_api.py - Settings/engine/
    # sessionmaker are process-wide lru_cache singletons, so this module needs
    # its own throwaway FORGE_DATA_DIR and cache-clear bracket.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-model-playground-test-")

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


def test_providers_and_credentials_require_a_session(client):
    assert client.get("/api/model-playground/providers").status_code == 401
    assert client.get("/api/model-playground/credentials").status_code == 401
    assert client.post("/api/model-playground/runs", json={"prompt": "hi", "targets": []}).status_code == 401


def test_providers_list_shows_both_v1_providers_unconfigured_by_default(authed_client):
    response = authed_client.get("/api/model-playground/providers")
    assert response.status_code == 200
    items = {p["provider"]: p for p in response.json()}
    assert set(items) == {"openai", "anthropic"}
    assert items["openai"]["configured"] is False
    assert items["anthropic"]["configured"] is False


def test_run_with_a_valid_but_unconfigured_provider_returns_400(authed_client):
    # Runs before any credential is created in this module - openai has no
    # credential configured yet, so this exercises the "provider_not_configured"
    # path (400), distinct from the schema-level "unknown model" path (422).
    response = authed_client.post(
        "/api/model-playground/runs",
        json={"prompt": "hi", "targets": [{"provider": "openai", "model": "gpt-4.1"}]},
    )
    assert response.status_code == 400


def test_create_credential_response_never_includes_the_api_key(authed_client):
    response = authed_client.post(
        "/api/model-playground/credentials",
        json={"provider": "openai", "label": "Test key", "api_key": "sk-do-not-leak"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "api_key" not in body
    assert "sk-do-not-leak" not in response.text
    assert body["provider"] == "openai"


def test_create_credential_unknown_provider_returns_422(authed_client):
    response = authed_client.post(
        "/api/model-playground/credentials", json={"provider": "made-up", "api_key": "x"}
    )
    assert response.status_code == 422


def test_list_credentials_reflects_created_credential(authed_client):
    authed_client.post(
        "/api/model-playground/credentials", json={"provider": "anthropic", "api_key": "anthropic-key"}
    )
    response = authed_client.get("/api/model-playground/credentials")
    assert response.status_code == 200
    providers = {c["provider"] for c in response.json()["items"]}
    assert "anthropic" in providers


def test_delete_missing_credential_returns_404(authed_client):
    assert authed_client.delete("/api/model-playground/credentials/does-not-exist").status_code == 404


def test_run_with_unknown_model_returns_422(authed_client):
    response = authed_client.post(
        "/api/model-playground/runs",
        json={"prompt": "hi", "targets": [{"provider": "openai", "model": "made-up-model"}]},
    )
    assert response.status_code == 422


def test_run_empty_targets_returns_422(authed_client):
    response = authed_client.post("/api/model-playground/runs", json={"prompt": "hi", "targets": []})
    assert response.status_code == 422


def test_run_over_cap_targets_returns_422(authed_client):
    targets = [{"provider": "openai", "model": "gpt-4.1"}] * 7
    response = authed_client.post("/api/model-playground/runs", json={"prompt": "hi", "targets": targets})
    assert response.status_code == 422


def test_run_partial_failure_returns_200_with_mixed_result_statuses(authed_client):
    authed_client.post("/api/model-playground/credentials", json={"provider": "openai", "api_key": "k1"})
    authed_client.post("/api/model-playground/credentials", json={"provider": "anthropic", "api_key": "k2"})
    _install_fake_adapter("openai", _FakeAdapter(error=RuntimeError("simulated failure")))
    _install_fake_adapter("anthropic", _FakeAdapter(text="anthropic ok"))

    response = authed_client.post(
        "/api/model-playground/runs",
        json={
            "prompt": "compare",
            "targets": [
                {"provider": "openai", "model": "gpt-4.1"},
                {"provider": "anthropic", "model": "claude-sonnet-5"},
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()
    by_provider = {r["provider"]: r for r in body["results"]}
    assert by_provider["openai"]["status"] == "error"
    assert by_provider["anthropic"]["status"] == "success"
    assert by_provider["anthropic"]["response_text"] == "anthropic ok"


def test_run_history_lifecycle(authed_client):
    _install_fake_adapter("openai", _FakeAdapter(text="history test"))
    created = authed_client.post(
        "/api/model-playground/runs",
        json={"prompt": "history test prompt", "targets": [{"provider": "openai", "model": "gpt-4.1"}]},
    ).json()

    list_response = authed_client.get("/api/model-playground/runs")
    assert list_response.status_code == 200
    assert any(r["id"] == created["id"] for r in list_response.json()["items"])

    get_response = authed_client.get(f"/api/model-playground/runs/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["prompt"] == "history test prompt"

    delete_response = authed_client.delete(f"/api/model-playground/runs/{created['id']}")
    assert delete_response.status_code == 204
    assert authed_client.get(f"/api/model-playground/runs/{created['id']}").status_code == 404


def test_get_missing_run_returns_404(authed_client):
    assert authed_client.get("/api/model-playground/runs/does-not-exist").status_code == 404
