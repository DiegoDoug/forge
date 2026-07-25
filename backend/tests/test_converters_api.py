"""Milestone 3 (Ingest provider integration) API tests.

Covers the one new additive endpoint (`GET /api/converters/providers`) and,
per `07_TESTING.md` §1's contract-preservation requirement, exercises every
pre-existing `/api/ingest/*` endpoint and `/api/converters/cron/parse`
end-to-end against the running app with Milestone 3's changes applied. This
repo has no captured pre-phase OpenAPI snapshot to literally byte-diff
against, so "contract preservation" here means: every documented existing
path/status-code/shape (per `docs/API.md` and the source as read during
`07_TESTING.md`'s drafting) still behaves identically. The OpenAPI check at
the bottom is a presence check against that same known set, not a diff
against a captured artifact — stated plainly rather than overclaimed.
"""

from __future__ import annotations

import io
import os
import tempfile
import time

import pytest


@pytest.fixture(scope="module")
def client():
    # Same isolation pattern as test_project_init_api.py: Settings/engine/
    # sessionmaker are process-wide lru_cache singletons, so this module
    # gets its own throwaway FORGE_DATA_DIR and clears those caches before
    # and after, so it can't leak state into (or inherit state from)
    # whichever other test module boots the real app in the same process.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-converters-test-")

    from app.main import create_app
    from starlette.testclient import TestClient

    app = create_app()
    with TestClient(app) as c:
        yield c

    if previous_data_dir is None:
        os.environ.pop("FORGE_DATA_DIR", None)
    else:
        os.environ["FORGE_DATA_DIR"] = previous_data_dir
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


def _wait_for_job_done(client, job_id: str, timeout: float = 10.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"/api/ingest/jobs/{job_id}")
        assert response.status_code == 200
        body = response.json()
        if body["status"] != "processing":
            return body
        time.sleep(0.05)
    raise AssertionError(f"Job {job_id} did not finish within {timeout}s")


# --- GET /api/converters/providers (new, additive) ---------------------------


def test_get_providers_requires_a_session(client):
    response = client.get("/api/converters/providers")
    assert response.status_code == 401


def test_setup_then_get_providers_returns_the_registered_markitdown_provider(client):
    setup_response = client.post("/api/setup", json={"master_password": "correct horse battery staple"})
    assert setup_response.status_code == 200

    response = client.get("/api/converters/providers")
    assert response.status_code == 200

    from app.services.ingest import formats

    body = response.json()
    assert len(body["providers"]) == 1
    provider = body["providers"][0]
    assert provider["slug"] == "markitdown"
    assert provider["output_format"] == "markdown"
    assert set(provider["input_extensions"]) == formats.KNOWN_EXTENSIONS


# --- Contract preservation: /api/converters/cron/parse -----------------------


def test_cron_parse_contract_unchanged(client):
    response = client.post("/api/converters/cron/parse", json={"expression": "0 12 * * *", "count": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "minute=0, hour=12, day of month=*, month=*, day of week=*"
    assert len(body["next_runs"]) == 3


def test_cron_parse_invalid_expression_contract_unchanged(client):
    response = client.post("/api/converters/cron/parse", json={"expression": "not a cron expression"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "app_error"


# --- Contract preservation: /api/ingest/* ------------------------------------


def test_ingest_formats_contract_unchanged(client):
    from app.services.ingest import formats

    response = client.get("/api/ingest/formats")
    assert response.status_code == 200
    assert set(response.json()["extensions"]) == formats.KNOWN_EXTENSIONS


def test_ingest_full_lifecycle_contract_unchanged(client):
    # Upload
    create_response = client.post(
        "/api/ingest/jobs",
        files=[("files", ("sample.txt", b"Hello Forge Milestone 3 test.\n", "text/plain"))],
    )
    assert create_response.status_code == 202
    job = create_response.json()
    job_id = job["id"]
    assert len(job["files"]) == 1
    file_id = job["files"][0]["id"]
    assert job["files"][0]["name"] == "sample.txt"
    assert job["files"][0]["markdown_name"] == "sample.md"

    # Poll until done
    job = _wait_for_job_done(client, job_id)
    assert job["status"] == "done"
    task = job["files"][0]
    assert task["status"] == "done"
    assert task["used_vision"] is False
    assert task["download_url"] == f"/api/ingest/jobs/{job_id}/files/{file_id}/download"
    assert job["download_all_url"] == f"/api/ingest/jobs/{job_id}/download"

    # Content preview
    content_response = client.get(f"/api/ingest/jobs/{job_id}/files/{file_id}/content")
    assert content_response.status_code == 200
    assert content_response.json()["markdown"] == "Hello Forge Milestone 3 test.\n"

    # Single-file download. `converter.py`'s `out_path.write_text(...)` uses
    # Python's default text-mode newline translation, which is a platform-
    # dependent, pre-existing characteristic of the unmodified pipeline (LF
    # stays LF on Linux/the real deployment target; CRLF on Windows dev
    # environments) — normalize before comparing so this test pins the
    # actual text content, not an incidental platform line-ending detail.
    download_response = client.get(f"/api/ingest/jobs/{job_id}/files/{file_id}/download")
    assert download_response.status_code == 200
    assert download_response.content.replace(b"\r\n", b"\n") == b"Hello Forge Milestone 3 test.\n"

    # Zip-all download
    zip_response = client.get(f"/api/ingest/jobs/{job_id}/download")
    assert zip_response.status_code == 200
    assert zip_response.headers["content-type"] == "application/zip"

    # Save to notes
    save_response = client.post(f"/api/ingest/jobs/{job_id}/files/{file_id}/save-to-notes", json={})
    assert save_response.status_code == 201
    note = save_response.json()
    assert note["title"] == "sample"
    assert note["content"] == "Hello Forge Milestone 3 test.\n"


def test_ingest_job_not_found_contract_unchanged(client):
    response = client.get("/api/ingest/jobs/does-not-exist")
    assert response.status_code == 404


def test_ingest_requires_a_session(client):
    # A fresh client, deliberately not reusing the module's authenticated
    # session cookie, to confirm auth is still enforced on this route set.
    from app.main import create_app
    from starlette.testclient import TestClient

    with TestClient(create_app(), cookies={}) as anon:
        response = anon.get("/api/ingest/formats")
        assert response.status_code == 401


# --- OpenAPI presence check (additive-only) ----------------------------------


def test_openapi_contains_every_pre_existing_path_plus_the_new_one(client):
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    pre_existing_paths_and_methods = {
        "/api/converters/cron/parse": {"post"},
        "/api/ingest/formats": {"get"},
        "/api/ingest/jobs": {"post"},
        "/api/ingest/jobs/{job_id}": {"get"},
        "/api/ingest/jobs/{job_id}/files/{file_id}/download": {"get"},
        "/api/ingest/jobs/{job_id}/files/{file_id}/content": {"get"},
        "/api/ingest/jobs/{job_id}/download": {"get"},
        "/api/ingest/jobs/{job_id}/files/{file_id}/save-to-notes": {"post"},
    }
    for path, methods in pre_existing_paths_and_methods.items():
        assert path in paths, f"pre-existing path {path} missing from OpenAPI schema"
        assert methods <= set(paths[path].keys()), f"pre-existing method(s) missing for {path}"

    assert "/api/converters/providers" in paths
    assert "get" in paths["/api/converters/providers"]
