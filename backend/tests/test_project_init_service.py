import json

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.errors import AppError, NotFoundError
from app.models import *  # noqa: F401,F403 (register every table on SQLModel.metadata)
from app.models.activity import ActivityLog
from app.services.project_init import service


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


FDK_CONFIG = {"phase_number": 9, "phase_name": "Knowledge Hub", "objective": "Unify Notes and Documents."}
AI_CONFIG = {
    "project_name": "acme-api",
    "description": "An API for Acme.",
    "tech_stack": ["FastAPI"],
    "output_files": ["CLAUDE.md"],
}


async def test_generate_persists_a_history_row(db_session):
    record, files = await service.generate(db_session, "fdk_phase", FDK_CONFIG)

    assert record.kind == "fdk_phase"
    assert record.name == "Knowledge Hub"
    assert json.loads(record.config) == FDK_CONFIG
    assert len(files) == 13


async def test_generate_writes_exactly_one_activity_log_row(db_session):
    from sqlmodel import select

    await service.generate(db_session, "ai_instructions", AI_CONFIG)

    result = await db_session.execute(select(ActivityLog))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].entity_type == "project_init_generation"


async def test_generate_rejects_invalid_config(db_session):
    with pytest.raises(AppError) as exc_info:
        await service.generate(db_session, "fdk_phase", {"phase_number": 0, "phase_name": "", "objective": ""})
    assert exc_info.value.status_code == 422


async def test_generate_rejects_ai_instructions_with_no_output_files(db_session):
    with pytest.raises(AppError) as exc_info:
        await service.generate(
            db_session, "ai_instructions", {"project_name": "x", "description": "y", "output_files": []}
        )
    assert exc_info.value.status_code == 422


async def test_render_zip_for_reproduces_the_same_files(db_session):
    record, files = await service.generate(db_session, "fdk_phase", FDK_CONFIG)

    _record, zip_bytes, filename = await service.render_zip_for(db_session, record.id)

    assert filename == "Phase-09-Knowledge-Hub.zip"
    assert len(zip_bytes) > 0

    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        assert set(archive.namelist()) == set(files.keys())


async def test_render_zip_for_missing_id_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await service.render_zip_for(db_session, "does-not-exist")


async def test_list_history_returns_newest_first_and_respects_limit(db_session):
    for i in range(3):
        await service.generate(db_session, "fdk_phase", {**FDK_CONFIG, "phase_name": f"Phase {i}"})

    history = await service.list_history(db_session, limit=2)

    assert len(history) == 2
    assert history[0].name == "Phase 2"
    assert history[1].name == "Phase 1"


async def test_delete_removes_the_row(db_session):
    record, _files = await service.generate(db_session, "fdk_phase", FDK_CONFIG)

    await service.delete(db_session, record.id)

    with pytest.raises(NotFoundError):
        await service.render_zip_for(db_session, record.id)


async def test_delete_missing_id_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await service.delete(db_session, "does-not-exist")
