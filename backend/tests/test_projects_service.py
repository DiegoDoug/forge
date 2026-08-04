from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select

from app.core.errors import AppError, NotFoundError
from app.models import *  # noqa: F401,F403 (register every table on SQLModel.metadata)
from app.models.document import Document
from app.models.note import Note
from app.models.secrets import Secret
from app.schemas.projects import ProjectCreateIn, ProjectUpdateIn
from app.services.model_playground import credentials as credentials_service
from app.services.model_playground.providers import PROVIDER_REGISTRY
from app.services.model_playground.providers.base import AdapterResult
from app.services.projects import service as projects_service


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


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


# --- CRUD --------------------------------------------------------------


async def test_create_and_get_project(db_session):
    project, counts = await projects_service.create_project(
        db_session, ProjectCreateIn(name="Client A", description="notes")
    )

    assert project.name == "Client A"
    assert project.archived is False
    assert counts.secret_count == 0 and counts.note_count == 0 and counts.document_count == 0

    fetched, _ = await projects_service.get_project(db_session, project.id)
    assert fetched.id == project.id


async def test_get_missing_project_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await projects_service.get_project(db_session, "does-not-exist")


async def test_list_projects_filters_by_archived(db_session):
    active, _ = await projects_service.create_project(db_session, ProjectCreateIn(name="Active"))
    archived, _ = await projects_service.create_project(db_session, ProjectCreateIn(name="Archived"))
    await projects_service.update_project(db_session, archived.id, ProjectUpdateIn(archived=True))

    active_list = await projects_service.list_projects(db_session, archived=False)
    archived_list = await projects_service.list_projects(db_session, archived=True)

    assert [p.id for p, _ in active_list] == [active.id]
    assert [p.id for p, _ in archived_list] == [archived.id]


async def test_update_project_partial_fields(db_session):
    project, _ = await projects_service.create_project(db_session, ProjectCreateIn(name="Original"))

    updated, _ = await projects_service.update_project(db_session, project.id, ProjectUpdateIn(description="new desc"))

    assert updated.name == "Original"  # untouched
    assert updated.description == "new desc"


# --- Counts --------------------------------------------------------------


async def test_counts_reflect_scoped_rows(db_session):
    project, _ = await projects_service.create_project(db_session, ProjectCreateIn(name="Counted"))

    db_session.add(Secret(name="s1", encrypted_value=b"x", project_id=project.id))
    db_session.add(Note(title="n1", project_id=project.id))
    db_session.add(Document(title="d1", project_id=project.id))
    db_session.add(Note(title="n2", project_id=None))  # unassigned, must not count
    await db_session.commit()

    _, counts = await projects_service.get_project(db_session, project.id)
    assert counts.secret_count == 1
    assert counts.note_count == 1
    assert counts.document_count == 1


# --- Delete unscopes, never destroys --------------------------------------


async def test_delete_project_unscopes_children_without_deleting_them(db_session):
    project, _ = await projects_service.create_project(db_session, ProjectCreateIn(name="Doomed"))
    secret = Secret(name="s1", encrypted_value=b"cipher", project_id=project.id)
    note = Note(title="n1", project_id=project.id)
    db_session.add(secret)
    db_session.add(note)
    await db_session.commit()

    await projects_service.delete_project(db_session, project.id)

    with pytest.raises(NotFoundError):
        await projects_service.get_project(db_session, project.id)

    reloaded_secret = (await db_session.execute(select(Secret).where(Secret.id == secret.id))).scalar_one()
    reloaded_note = (await db_session.execute(select(Note).where(Note.id == note.id))).scalar_one()
    assert reloaded_secret.project_id is None
    assert reloaded_secret.name == "s1"
    assert reloaded_secret.encrypted_value == b"cipher"
    assert reloaded_note.project_id is None
    assert reloaded_note.title == "n1"


async def test_delete_missing_project_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await projects_service.delete_project(db_session, "does-not-exist")


# --- AI run delegation -----------------------------------------------------


async def test_run_project_prompt_with_no_default_configured_raises(db_session):
    project, _ = await projects_service.create_project(db_session, ProjectCreateIn(name="No AI"))

    with pytest.raises(AppError) as exc_info:
        await projects_service.run_project_prompt(db_session, project.id, "hello")
    assert exc_info.value.code == "project_ai_not_configured"


async def test_run_project_prompt_with_unconfigured_credential_raises_provider_not_configured(db_session):
    project, _ = await projects_service.create_project(
        db_session, ProjectCreateIn(name="Configured", default_provider="openai", default_model="gpt-4.1")
    )

    with pytest.raises(AppError) as exc_info:
        await projects_service.run_project_prompt(db_session, project.id, "hello")
    assert exc_info.value.code == "provider_not_configured"


async def test_run_project_prompt_success_stamps_project_id_and_is_listed(db_session):
    project, _ = await projects_service.create_project(
        db_session, ProjectCreateIn(name="Configured", default_provider="openai", default_model="gpt-4.1")
    )
    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k1")
    object.__setattr__(PROVIDER_REGISTRY["openai"], "adapter", _FakeAdapter(text="ran it"))

    run = await projects_service.run_project_prompt(db_session, project.id, "hello project")

    assert run.project_id == project.id
    assert run.results[0].status == "success"
    assert run.results[0].response_text == "ran it"

    runs = await projects_service.list_project_runs(db_session, project.id)
    assert [r.id for r in runs] == [run.id]


async def test_list_project_runs_missing_project_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await projects_service.list_project_runs(db_session, "does-not-exist")
