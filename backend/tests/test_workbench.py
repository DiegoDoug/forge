from __future__ import annotations

import json
import os
import tempfile

# This is the first test module in the suite that boots the real FastAPI app
# (to exercise routes/workbench.py end-to-end) - Settings and the DB engine
# are both @lru_cache'd process-wide and read on first import/use. Give it
# its own throwaway data dir so repeated test runs don't collide with a
# previously-completed /api/setup from an earlier run, mirroring the pattern
# conftest.py already uses for FORGE_DATA_DIR/FORGE_MASTER_KEY.
os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-workbench-test-")

import pytest  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.core.errors import AppError  # noqa: E402
from app.main import app  # noqa: E402
from app.models import *  # noqa: E402,F401,F403 (register every table on SQLModel.metadata)
from app.models.activity import ActivityLog  # noqa: E402
from app.models.note import Note  # noqa: E402
from app.services import workbench as workbench_service  # noqa: E402

# ---------------------------------------------------------------------------
# Unit tests - services/workbench.py, each against its own isolated in-memory DB
# ---------------------------------------------------------------------------


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


async def test_get_layout_creates_default_row_on_first_access(db_session):
    layout = await workbench_service.get_layout(db_session)
    assert layout.id == 1
    assert json.loads(layout.panels) == workbench_service.DEFAULT_LAYOUT_PANELS
    assert json.loads(layout.pinned_tools) == workbench_service.DEFAULT_PINNED_TOOLS


async def test_get_layout_is_idempotent(db_session):
    first = await workbench_service.get_layout(db_session)
    second = await workbench_service.get_layout(db_session)
    assert first.id == second.id == 1


async def test_update_layout_accepts_unrecognized_panel_type(db_session):
    # Load-bearing: proves panel `type` is NOT enum-validated (ADR-0002 /
    # 06_API.md §2) - an unregistered type is structurally valid and simply
    # renders nothing until a matching frontend panel exists.
    layout = await workbench_service.update_layout(
        db_session, panels=[{"type": "recent_projects", "visible": False}], pinned_tools=[]
    )
    assert json.loads(layout.panels) == [{"type": "recent_projects", "visible": False}]


async def test_update_layout_rejects_duplicate_panel_type(db_session):
    with pytest.raises(AppError) as exc_info:
        await workbench_service.update_layout(
            db_session,
            panels=[{"type": "recent_notes", "visible": True}, {"type": "recent_notes", "visible": False}],
            pinned_tools=[],
        )
    assert exc_info.value.status_code == 422


async def test_update_layout_rejects_panel_missing_a_field(db_session):
    with pytest.raises(AppError) as exc_info:
        await workbench_service.update_layout(db_session, panels=[{"type": "recent_notes"}], pinned_tools=[])
    assert exc_info.value.status_code == 422


async def test_update_layout_rejects_unknown_pinned_tool(db_session):
    with pytest.raises(AppError) as exc_info:
        await workbench_service.update_layout(db_session, panels=[], pinned_tools=["not_a_real_tool"])
    assert exc_info.value.status_code == 422


async def test_update_layout_accepts_an_unavailable_pinned_tool(db_session):
    layout = await workbench_service.update_layout(db_session, panels=[], pinned_tools=["prompt_studio"])
    assert json.loads(layout.pinned_tools) == ["prompt_studio"]


async def test_reset_layout_restores_the_default_layout(db_session):
    await workbench_service.update_layout(
        db_session, panels=[{"type": "recent_notes", "visible": False}], pinned_tools=["secrets"]
    )
    layout = await workbench_service.reset_layout(db_session)
    assert json.loads(layout.panels) == workbench_service.DEFAULT_LAYOUT_PANELS
    assert len(json.loads(layout.panels)) == 5
    assert json.loads(layout.pinned_tools) == workbench_service.DEFAULT_PINNED_TOOLS
    assert len(json.loads(layout.pinned_tools)) == 6


async def test_get_workbench_matches_dashboard_shape_minus_recent_secrets(db_session):
    db_session.add(ActivityLog(action="created", entity_type="note", entity_id="abc", summary="Created a note"))
    db_session.add(Note(title="Hello", content="world", color="#fde68a"))
    await db_session.commit()

    data = (await workbench_service.get_workbench(db_session))["data"]

    assert "recent_secrets" not in data
    assert set(data.keys()) == {"version", "storage", "recent_activity", "recent_notes"}
    assert set(data["storage"].keys()) == {
        "database_bytes",
        "disk_total_bytes",
        "disk_used_bytes",
        "disk_free_bytes",
    }
    assert len(data["recent_activity"]) == 1
    assert data["recent_activity"][0]["action"] == "created"
    assert len(data["recent_notes"]) == 1
    assert data["recent_notes"][0]["title"] == "Hello"


# ---------------------------------------------------------------------------
# Integration tests - routes/workbench.py, against the real app over one
# shared TestClient (module-scoped, matching the single-instance nature of
# the underlying single-row workbench_layout table). Defined top-to-bottom in
# the order they must run: the first relies on no session existing yet, the
# rest run after /api/setup has established one.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_get_workbench_requires_a_session(client):
    response = client.get("/api/workbench")
    assert response.status_code == 401


def test_setup_then_get_workbench_returns_full_shape(client):
    setup_response = client.post("/api/setup", json={"master_password": "correct horse battery staple"})
    assert setup_response.status_code == 200

    response = client.get("/api/workbench")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"layout", "data"}
    assert "recent_secrets" not in body["data"]
    assert len(body["layout"]["tool_catalog"]) == len(workbench_service.WORKBENCH_TOOL_KEYS)


def test_put_layout_valid_payload_is_reflected_on_get(client):
    put_response = client.put(
        "/api/workbench/layout",
        json={"panels": [{"type": "recent_notes", "visible": False}], "pinned_tools": ["secrets", "search"]},
    )
    assert put_response.status_code == 200
    assert put_response.json()["panels"] == [{"type": "recent_notes", "visible": False}]

    get_response = client.get("/api/workbench")
    assert get_response.json()["layout"]["panels"] == [{"type": "recent_notes", "visible": False}]


def test_put_layout_rejects_unknown_pinned_tool(client):
    response = client.put("/api/workbench/layout", json={"panels": [], "pinned_tools": ["not_a_real_tool"]})
    assert response.status_code == 422


def test_put_layout_accepts_unrecognized_panel_type(client):
    # Confirms the §2 not-enum-validated behavior at the route level, not
    # just the service level (06_API.md §2).
    response = client.put(
        "/api/workbench/layout",
        json={"panels": [{"type": "recent_projects", "visible": False}], "pinned_tools": []},
    )
    assert response.status_code == 200
    assert response.json()["panels"] == [{"type": "recent_projects", "visible": False}]


def test_reset_layout_restores_defaults_confirmed_via_get(client):
    reset_response = client.post("/api/workbench/layout/reset")
    assert reset_response.status_code == 200
    assert reset_response.json()["panels"] == workbench_service.DEFAULT_LAYOUT_PANELS

    get_response = client.get("/api/workbench")
    assert get_response.json()["layout"]["panels"] == workbench_service.DEFAULT_LAYOUT_PANELS
    pinned_keys = [p["key"] for p in get_response.json()["layout"]["pinned_tools"]]
    assert pinned_keys == workbench_service.DEFAULT_PINNED_TOOLS
