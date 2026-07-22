from __future__ import annotations

import io
import os
import tempfile
import zipfile

import pytest


@pytest.fixture(scope="module")
def client():
    # This module boots the real FastAPI app end-to-end, same as
    # test_workbench.py. Settings/engine/sessionmaker are process-wide
    # lru_cache singletons (app/core/config.py, app/database/session.py), so
    # sharing a pytest process with another module that does the same thing
    # would otherwise leak state (a completed /api/setup, an on-disk SQLite
    # file) across module boundaries regardless of which throwaway
    # FORGE_DATA_DIR each module sets. Clear the caches before this module's
    # tests so it gets its own isolated database, then restore the env var
    # and clear the caches again afterward so whichever module boots the
    # real app next (test_workbench.py, collected - and so already holding
    # its own FORGE_DATA_DIR in the environment - before this fixture runs)
    # re-resolves its own settings/engine instead of inheriting this
    # module's leftover throwaway directory.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-project-init-test-")

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


def test_catalog_requires_a_session(client):
    response = client.get("/api/project-init/catalog")
    assert response.status_code == 401


def test_setup_then_get_catalog_returns_both_kinds(client):
    setup_response = client.post("/api/setup", json={"master_password": "correct horse battery staple"})
    assert setup_response.status_code == 200

    response = client.get("/api/project-init/catalog")
    assert response.status_code == 200
    kinds = {k["kind"] for k in response.json()["kinds"]}
    assert kinds == {"fdk_phase", "ai_instructions"}


def test_generate_fdk_phase_returns_correct_file_count(client):
    response = client.post(
        "/api/project-init/generate",
        json={
            "kind": "fdk_phase",
            "config": {"phase_number": 9, "phase_name": "Knowledge Hub", "objective": "Unify Notes and Documents."},
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["kind"] == "fdk_phase"
    assert body["name"] == "Knowledge Hub"
    assert body["file_count"] == 13


def test_generate_ai_instructions_returns_only_selected_file_count(client):
    response = client.post(
        "/api/project-init/generate",
        json={
            "kind": "ai_instructions",
            "config": {
                "project_name": "acme-api",
                "description": "An API for Acme.",
                "tech_stack": ["FastAPI", "Postgres"],
                "output_files": ["CLAUDE.md", "AGENTS.md"],
            },
        },
    )
    assert response.status_code == 201
    assert response.json()["file_count"] == 2


def test_generate_missing_required_field_returns_422(client):
    response = client.post(
        "/api/project-init/generate",
        json={"kind": "fdk_phase", "config": {"phase_number": 9}},
    )
    assert response.status_code == 422


def test_generate_ai_instructions_with_no_output_files_returns_422(client):
    response = client.post(
        "/api/project-init/generate",
        json={
            "kind": "ai_instructions",
            "config": {"project_name": "x", "description": "y", "output_files": []},
        },
    )
    assert response.status_code == 422


def test_download_returns_a_valid_zip_with_expected_files(client):
    generate_response = client.post(
        "/api/project-init/generate",
        json={
            "kind": "fdk_phase",
            "config": {"phase_number": 5, "phase_name": "Model Playground", "objective": "Test providers."},
        },
    )
    generation_id = generate_response.json()["id"]

    response = client.get(f"/api/project-init/{generation_id}/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "Phase-05-Model-Playground.zip" in response.headers["content-disposition"]

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = archive.namelist()
        assert len(names) == 13
        assert all(name.startswith("Phase-05-Model-Playground/") for name in names)


def test_download_missing_id_returns_404(client):
    response = client.get("/api/project-init/does-not-exist/download")
    assert response.status_code == 404


def test_history_includes_prior_generations(client):
    response = client.get("/api/project-init/history")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1


def test_delete_then_download_returns_404(client):
    generate_response = client.post(
        "/api/project-init/generate",
        json={
            "kind": "ai_instructions",
            "config": {"project_name": "temp-project", "description": "Temp.", "output_files": ["instructions.md"]},
        },
    )
    generation_id = generate_response.json()["id"]

    delete_response = client.delete(f"/api/project-init/{generation_id}")
    assert delete_response.status_code == 204

    download_response = client.get(f"/api/project-init/{generation_id}/download")
    assert download_response.status_code == 404
