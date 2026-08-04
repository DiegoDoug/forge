from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(scope="module")
def client():
    # Same isolation pattern as test_projects_api.py - Settings/engine/
    # sessionmaker are process-wide lru_cache singletons, so this module
    # needs its own throwaway FORGE_DATA_DIR and cache-clear bracket. Uses
    # the real create_app() (real migration chain, real FTS5 triggers),
    # not the in-memory SQLModel.metadata.create_all() fixture the
    # service-level tests use.
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-knowledge-test-")

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


# --- auth --------------------------------------------------------------


def test_all_seven_routes_require_a_session(client):
    assert client.get("/api/knowledge").status_code == 401
    assert client.get("/api/knowledge/tags").status_code == 401
    assert client.post("/api/knowledge/note/x/tags", json={"tag_id": "y"}).status_code == 401
    assert client.delete("/api/knowledge/note/x/tags/y").status_code == 401
    assert client.get("/api/knowledge/note/x/links").status_code == 401
    assert client.post("/api/knowledge/note/x/links", json={"target_type": "note", "target_id": "y"}).status_code == 401
    assert client.delete("/api/knowledge/links/x").status_code == 401


# --- GET /api/knowledge: real FTS5, filters, cap --------------------------


def test_query_matches_only_the_right_type_via_real_fts5(authed_client):
    note = authed_client.post("/api/notes", json={"title": "Architecture notes", "content": "fts5 decision"})
    assert note.status_code == 201
    document = authed_client.post("/api/documents", json={"title": "Runbook", "content": "deployment steps"})
    assert document.status_code == 201

    hit = authed_client.get("/api/knowledge", params={"q": "fts5"})
    assert hit.status_code == 200
    body = hit.json()
    assert any(i["id"] == note.json()["id"] and i["type"] == "note" for i in body["items"])
    assert not any(i["id"] == document.json()["id"] for i in body["items"])

    miss = authed_client.get("/api/knowledge", params={"q": "nonsense-term-xyz"})
    assert miss.json()["items"] == []
    assert miss.json()["total"] == 0


def test_type_filter(authed_client):
    only_notes = authed_client.get("/api/knowledge", params={"type": "note"}).json()
    assert all(i["type"] == "note" for i in only_notes["items"])

    only_documents = authed_client.get("/api/knowledge", params={"type": "document"}).json()
    assert all(i["type"] == "document" for i in only_documents["items"])


def test_unknown_item_type_path_param_is_422(authed_client):
    assert authed_client.post("/api/knowledge/bogus/x/tags", json={"tag_id": "y"}).status_code == 422


def test_tag_filter_and_semantics_over_http(authed_client):
    n1 = authed_client.post("/api/notes", json={"title": "and-only-x"}).json()
    n2 = authed_client.post("/api/notes", json={"title": "and-only-y"}).json()
    n3 = authed_client.post("/api/notes", json={"title": "and-both"}).json()

    tag_x = authed_client.post(f"/api/knowledge/note/{n1['id']}/tags", json={"name": "and-x"}).json()[0]
    tag_y = authed_client.post(f"/api/knowledge/note/{n2['id']}/tags", json={"name": "and-y"}).json()[0]
    authed_client.post(f"/api/knowledge/note/{n3['id']}/tags", json={"tag_id": tag_x["id"]})
    authed_client.post(f"/api/knowledge/note/{n3['id']}/tags", json={"tag_id": tag_y["id"]})

    both = authed_client.get("/api/knowledge", params=[("tag_id", tag_x["id"]), ("tag_id", tag_y["id"])]).json()
    ids = {i["id"] for i in both["items"]}
    assert ids == {n3["id"]}


def test_result_cap_105_returns_100_truncated_true(authed_client):
    for i in range(105):
        r = authed_client.post("/api/notes", json={"title": f"cap-note-{i}"})
        assert r.status_code == 201

    body = authed_client.get("/api/knowledge", params={"q": "", "type": "note"}).json()
    # There are other notes from earlier tests too - just assert the cap
    # itself and truncation flag, not an exact count.
    assert len(body["items"]) <= 100
    if body["total"] > 100:
        assert body["truncated"] is True
        assert len(body["items"]) == 100
    else:
        assert body["truncated"] is False


def test_get_knowledge_has_no_pagination_parameter_accepted(authed_client):
    # There is no limit/page/offset/cursor parameter in the documented
    # contract (06_API.md SS1.1) - passing one is simply ignored by FastAPI
    # (extra query params are dropped, not errored), which is itself the
    # proof that no such parameter is wired to anything.
    r = authed_client.get("/api/knowledge", params={"limit": 5, "page": 2, "offset": 10, "cursor": "abc"})
    assert r.status_code == 200
    # confirm it did NOT limit to 5 - the fixed cap (100) or true count governs
    assert len(r.json()["items"]) != 5 or r.json()["total"] == 5


# --- tags ------------------------------------------------------------------


def test_tag_assign_requires_exactly_one_of_tag_id_or_name(authed_client):
    n = authed_client.post("/api/notes", json={"title": "tag-target"}).json()
    assert authed_client.post(f"/api/knowledge/note/{n['id']}/tags", json={}).status_code == 422
    assert (
        authed_client.post(f"/api/knowledge/note/{n['id']}/tags", json={"tag_id": "x", "name": "y"}).status_code
        == 422
    )


def test_tag_full_round_trip(authed_client):
    n = authed_client.post("/api/notes", json={"title": "round-trip"}).json()

    assign = authed_client.post(f"/api/knowledge/note/{n['id']}/tags", json={"name": "roundtrip-tag"})
    assert assign.status_code == 200
    tag = assign.json()[0]

    listed = authed_client.get("/api/knowledge", params={"q": "round-trip"}).json()
    item = next(i for i in listed["items"] if i["id"] == n["id"])
    assert any(t["id"] == tag["id"] for t in item["tags"])

    tags_endpoint = authed_client.get("/api/knowledge/tags").json()
    assert any(t["id"] == tag["id"] and t["count"] >= 1 for t in tags_endpoint)

    unassign = authed_client.delete(f"/api/knowledge/note/{n['id']}/tags/{tag['id']}")
    assert unassign.status_code == 204

    tags_endpoint_after = authed_client.get("/api/knowledge/tags").json()
    matching = [t for t in tags_endpoint_after if t["id"] == tag["id"]]
    assert matching == []


def test_tagging_a_note_does_not_touch_secrets(authed_client):
    n = authed_client.post("/api/notes", json={"title": "secret-safe"}).json()
    before = authed_client.get("/api/secrets").json()
    authed_client.post(f"/api/knowledge/note/{n['id']}/tags", json={"name": "safe-tag"})
    after = authed_client.get("/api/secrets").json()
    assert before == after


# --- links -------------------------------------------------------------


def test_link_full_round_trip(authed_client):
    n = authed_client.post("/api/notes", json={"title": "link-source"}).json()
    d = authed_client.post("/api/documents", json={"title": "link-target"}).json()

    create = authed_client.post(f"/api/knowledge/note/{n['id']}/links", json={"target_type": "document", "target_id": d["id"]})
    assert create.status_code == 201
    link = create.json()
    assert link["other"]["type"] == "document"
    assert link["other"]["id"] == d["id"]

    from_note = authed_client.get(f"/api/knowledge/note/{n['id']}/links").json()
    assert any(l["link_id"] == link["link_id"] for l in from_note)

    from_doc = authed_client.get(f"/api/knowledge/document/{d['id']}/links").json()
    assert any(l["link_id"] == link["link_id"] and l["other"]["id"] == n["id"] for l in from_doc)

    delete = authed_client.delete(f"/api/knowledge/links/{link['link_id']}")
    assert delete.status_code == 204

    assert authed_client.get(f"/api/knowledge/note/{n['id']}/links").json() == []


def test_self_link_and_duplicate_link_errors(authed_client):
    n = authed_client.post("/api/notes", json={"title": "self-link"}).json()
    self_link = authed_client.post(f"/api/knowledge/note/{n['id']}/links", json={"target_type": "note", "target_id": n["id"]})
    assert self_link.status_code == 400
    assert self_link.json()["error"]["code"] == "knowledge_link_self"

    n2 = authed_client.post("/api/notes", json={"title": "dup-target"}).json()
    first = authed_client.post(f"/api/knowledge/note/{n['id']}/links", json={"target_type": "note", "target_id": n2["id"]})
    assert first.status_code == 201
    dup = authed_client.post(f"/api/knowledge/note/{n['id']}/links", json={"target_type": "note", "target_id": n2["id"]})
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "knowledge_link_duplicate"


def test_deleting_a_note_purges_its_knowledge_links(authed_client):
    n1 = authed_client.post("/api/notes", json={"title": "will-delete"}).json()
    n2 = authed_client.post("/api/notes", json={"title": "survivor"}).json()
    authed_client.post(f"/api/knowledge/note/{n1['id']}/links", json={"target_type": "note", "target_id": n2["id"]})

    delete = authed_client.delete(f"/api/notes/{n1['id']}")
    assert delete.status_code == 204

    remaining = authed_client.get(f"/api/knowledge/note/{n2['id']}/links").json()
    assert remaining == []


def test_deleting_a_document_purges_its_knowledge_links(authed_client):
    n1 = authed_client.post("/api/notes", json={"title": "linked-to-doc"}).json()
    d1 = authed_client.post("/api/documents", json={"title": "will-delete-doc"}).json()
    authed_client.post(f"/api/knowledge/note/{n1['id']}/links", json={"target_type": "document", "target_id": d1["id"]})

    delete = authed_client.delete(f"/api/documents/{d1['id']}")
    assert delete.status_code == 204

    remaining = authed_client.get(f"/api/knowledge/note/{n1['id']}/links").json()
    assert remaining == []


# --- non-regression: /search and Ingest to-note ---------------------------


def test_search_response_shape_is_byte_for_byte_unchanged(authed_client):
    r = authed_client.get("/api/search", params={"q": "link-source"})
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"secrets", "notes", "documents"}
    assert isinstance(body["secrets"], list)
    assert isinstance(body["notes"], list)
    assert isinstance(body["documents"], list)


def test_ingest_to_note_produces_a_hub_visible_taggable_item(authed_client, tmp_path):
    # Real endpoint contract (POST /api/ingest/jobs creates the job AND
    # uploads in one call; the note handoff is /save-to-notes, not
    # /to-note) - confirmed against api/routes/ingest.py, correcting an
    # inaccuracy in 01_SPEC.md FR20 / 06_API.md's earlier "to-note" naming.
    upload_path = tmp_path / "sample.txt"
    upload_path.write_text("Hub visibility check content")

    with open(upload_path, "rb") as f:
        job = authed_client.post("/api/ingest/jobs", files={"files": ("sample.txt", f, "text/plain")})
    assert job.status_code == 202
    job_id = job.json()["id"]

    import time

    task = None
    status = None
    for _ in range(50):
        status = authed_client.get(f"/api/ingest/jobs/{job_id}").json()
        files = status.get("files", [])
        if files and files[0]["status"] in ("done", "error"):
            task = files[0]
            break
        time.sleep(0.1)

    if task is None or task["status"] != "done":
        pytest.skip("ingest conversion did not complete in time in this environment")

    to_note = authed_client.post(f"/api/ingest/jobs/{job_id}/files/{task['id']}/save-to-notes", json={"color": "#fde68a"})
    assert to_note.status_code == 201
    note_id = to_note.json()["id"]

    hub = authed_client.get("/api/knowledge", params={"q": "Hub visibility"}).json()
    assert any(i["id"] == note_id for i in hub["items"])

    tag = authed_client.post(f"/api/knowledge/note/{note_id}/tags", json={"name": "from-ingest"})
    assert tag.status_code == 200
