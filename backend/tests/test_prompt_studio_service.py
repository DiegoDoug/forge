import json

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select

from app.core.errors import NotFoundError
from app.models import *  # noqa: F401,F403 (register every table on SQLModel.metadata)
from app.models.activity import ActivityLog
from app.schemas.prompt_studio import PromptCreate, PromptUpdateContent, PromptUpdateMeta
from app.services.prompt_studio import service


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


VAR = {"name": "audience", "type": "string", "required": True}


async def _create(session, name="Summary", body="Write for ${audience}.", variables=None, tags=None):
    data = PromptCreate(name=name, body=body, variables=variables or [VAR], tags=tags or [])
    return await service.create(session, data)


async def test_create_starts_at_version_1_with_one_version_row(db_session):
    prompt = await _create(db_session)

    assert prompt.version_number == 1
    versions = await service.list_versions(db_session, prompt.id)
    assert len(versions) == 1
    assert versions[0].version_number == 1
    assert versions[0].note == "Initial version"
    assert versions[0].body == prompt.body


async def test_create_writes_exactly_one_activity_log_row(db_session):
    await _create(db_session)

    result = await db_session.execute(select(ActivityLog))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].entity_type == "prompt"
    assert rows[0].action == "created"


async def test_get_missing_id_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await service.get(db_session, "does-not-exist")


async def test_list_prompts_filters_by_search(db_session):
    await _create(db_session, name="Code Review", body="Review ${audience}'s code.")
    await _create(db_session, name="Commit Message", body="Write for ${audience}.")

    results = await service.list_prompts(db_session, search="Code")
    assert len(results) == 1
    assert results[0].name == "Code Review"


async def test_list_prompts_filters_by_tag(db_session):
    await _create(db_session, name="A", tags=["work"])
    await _create(db_session, name="B", tags=["personal"])

    results = await service.list_prompts(db_session, tag="work")
    assert len(results) == 1
    assert results[0].name == "A"


async def test_update_metadata_does_not_bump_version_or_create_a_version_row(db_session):
    prompt = await _create(db_session)

    updated = await service.update_metadata(db_session, prompt.id, PromptUpdateMeta(name="New name"))

    assert updated.version_number == 1
    assert updated.name == "New name"
    versions = await service.list_versions(db_session, prompt.id)
    assert len(versions) == 1  # still just the initial version


async def test_update_metadata_partial_payload_leaves_other_fields_untouched(db_session):
    prompt = await _create(db_session, name="Original", tags=["a"])

    updated = await service.update_metadata(db_session, prompt.id, PromptUpdateMeta(name="Renamed"))

    assert updated.name == "Renamed"
    assert json.loads(updated.tags_json) == ["a"]


async def test_update_content_bumps_version_and_creates_a_new_version_row(db_session):
    prompt = await _create(db_session)

    updated = await service.update_content(
        db_session, prompt.id, PromptUpdateContent(body="New body for ${audience}.", variables=[VAR])
    )

    assert updated.version_number == 2
    assert updated.body == "New body for ${audience}."
    versions = await service.list_versions(db_session, prompt.id)
    assert len(versions) == 2
    assert versions[0].version_number == 2
    assert versions[0].note == "Edited"
    assert versions[1].version_number == 1


async def test_update_content_twice_produces_two_new_versions(db_session):
    prompt = await _create(db_session)

    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="v2 ${audience}", variables=[VAR]))
    updated = await service.update_content(
        db_session, prompt.id, PromptUpdateContent(body="v3 ${audience}", variables=[VAR])
    )

    assert updated.version_number == 3
    versions = await service.list_versions(db_session, prompt.id)
    assert [v.version_number for v in versions] == [3, 2, 1]


async def test_delete_cascades_to_versions(db_session):
    prompt = await _create(db_session)
    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="v2 ${audience}", variables=[VAR]))

    await service.delete(db_session, prompt.id)

    result = await db_session.execute(select(PromptVersion).where(PromptVersion.prompt_id == prompt.id))
    assert result.scalars().all() == []
    with pytest.raises(NotFoundError):
        await service.get(db_session, prompt.id)


async def test_delete_missing_id_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await service.delete(db_session, "does-not-exist")


async def test_delete_activity_log_captures_name_before_row_is_gone(db_session):
    prompt = await _create(db_session, name="Doomed")

    await service.delete(db_session, prompt.id)

    result = await db_session.execute(select(ActivityLog).where(ActivityLog.action == "deleted"))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert "Doomed" in rows[0].summary


async def test_duplicate_creates_independent_prompt_with_its_own_version_1(db_session):
    source = await _create(db_session, name="Original")

    duplicate = await service.duplicate(db_session, source.id)

    assert duplicate.id != source.id
    assert duplicate.name == "Original (copy)"
    assert duplicate.version_number == 1
    assert duplicate.body == source.body
    versions = await service.list_versions(db_session, duplicate.id)
    assert len(versions) == 1
    assert "Duplicated from" in versions[0].note


async def test_duplicate_is_unaffected_by_deleting_the_source(db_session):
    source = await _create(db_session, name="Original")
    duplicate = await service.duplicate(db_session, source.id)

    await service.delete(db_session, source.id)

    still_there = await service.get(db_session, duplicate.id)
    assert still_there.id == duplicate.id


async def test_get_version_cross_prompt_lookup_raises_not_found(db_session):
    prompt_a = await _create(db_session, name="A")
    prompt_b = await _create(db_session, name="B")
    versions_a = await service.list_versions(db_session, prompt_a.id)

    with pytest.raises(NotFoundError):
        await service.get_version(db_session, prompt_b.id, versions_a[0].id)


async def test_restore_snapshots_current_first_and_never_reuses_a_version_number(db_session):
    prompt = await _create(db_session, body="v1 ${audience}")
    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="v2 ${audience}", variables=[VAR]))
    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="v3 ${audience}", variables=[VAR]))
    versions = await service.list_versions(db_session, prompt.id)
    v1 = next(v for v in versions if v.version_number == 1)

    restored = await service.restore_version(db_session, prompt.id, v1.id)

    assert restored.version_number == 4  # never re-uses "1", moves forward
    assert restored.body == "v1 ${audience}"
    all_versions = await service.list_versions(db_session, prompt.id)
    assert [v.version_number for v in all_versions] == [4, 3, 2, 1]  # nothing lost


async def test_restoring_again_to_a_different_version_preserves_every_prior_version(db_session):
    prompt = await _create(db_session, body="v1 ${audience}")
    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="v2 ${audience}", variables=[VAR]))
    versions = await service.list_versions(db_session, prompt.id)
    v1 = next(v for v in versions if v.version_number == 1)
    v2 = next(v for v in versions if v.version_number == 2)

    await service.restore_version(db_session, prompt.id, v1.id)  # -> v3
    await service.restore_version(db_session, prompt.id, v2.id)  # -> v4

    all_versions = await service.list_versions(db_session, prompt.id)
    assert [v.version_number for v in all_versions] == [4, 3, 2, 1]


async def test_update_a_then_update_a_again_is_not_collapsed_into_one_version(db_session):
    prompt = await _create(db_session)
    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="x ${audience}", variables=[VAR]))
    await service.update_content(db_session, prompt.id, PromptUpdateContent(body="y ${audience}", variables=[VAR]))

    versions = await service.list_versions(db_session, prompt.id)
    assert len(versions) == 3
