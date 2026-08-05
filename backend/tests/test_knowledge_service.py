from __future__ import annotations

import inspect

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.errors import AppError, NotFoundError
from app.models import *  # noqa: F401,F403 (register every table on SQLModel.metadata)
from app.models.document import Document
from app.models.note import Note
from app.models.secrets import Tag
from app.schemas.knowledge import KNOWLEDGE_RESULT_LIMIT
from app.services.knowledge import service as knowledge_service


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


async def _make_note(session, title="Note", content="", **kwargs) -> Note:
    note = Note(title=title, content=content, **kwargs)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def _make_document(session, title="Doc", content="", **kwargs) -> Document:
    document = Document(title=title, content=content, **kwargs)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def _make_tag(session, name: str) -> Tag:
    tag = Tag(name=name)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


# --- list_knowledge: merging, filters, FTS delegation -----------------------


async def test_list_knowledge_merges_notes_and_documents_sorted_by_updated_at(db_session):
    import asyncio

    n = await _make_note(db_session, title="N1")
    await asyncio.sleep(0.01)
    d = await _make_document(db_session, title="D1")

    items, total, truncated = await knowledge_service.list_knowledge(db_session)
    assert total == 2
    assert not truncated
    assert [i.type for i in items] == ["document", "note"]
    assert items[0].id == d.id
    assert items[1].id == n.id


async def test_list_knowledge_q_delegates_to_existing_fts_functions(db_session, monkeypatch):
    calls = []

    async def fake_search_notes(session, query):
        calls.append(("notes", query))
        return []

    async def fake_search_documents(session, query):
        calls.append(("documents", query))
        return []

    from app.services.documents import service as documents_service
    from app.services.notes import service as notes_service

    monkeypatch.setattr(notes_service, "search_notes", fake_search_notes)
    monkeypatch.setattr(documents_service, "search_documents", fake_search_documents)

    await knowledge_service.list_knowledge(db_session, q="hello")
    assert ("notes", "hello") in calls
    assert ("documents", "hello") in calls


# Real-FTS5 matching (a q= query actually finding the right type and
# excluding a non-matching term) is exercised at the API layer
# (test_knowledge_api.py), not here: the FTS5 virtual tables/triggers are
# created only by the real Alembic migration chain, not by
# SQLModel.metadata.create_all() - this fixture's in-memory schema has no
# notes_fts/documents_fts table, matching every other *_service.py test
# module's same constraint.


async def test_list_knowledge_type_filter(db_session):
    await _make_note(db_session)
    await _make_document(db_session)

    items, total, _ = await knowledge_service.list_knowledge(db_session, item_type="note")
    assert total == 1
    assert items[0].type == "note"

    items, total, _ = await knowledge_service.list_knowledge(db_session, item_type="document")
    assert total == 1
    assert items[0].type == "document"


async def test_list_knowledge_tag_filter_uses_and_semantics(db_session):
    tag_x = await _make_tag(db_session, "x")
    tag_y = await _make_tag(db_session, "y")

    only_x = await _make_note(db_session, title="only-x")
    only_y = await _make_note(db_session, title="only-y")
    both = await _make_note(db_session, title="both")

    await knowledge_service.add_tag(db_session, "note", only_x.id, tag_id=tag_x.id, name=None, color="#000")
    await knowledge_service.add_tag(db_session, "note", only_y.id, tag_id=tag_y.id, name=None, color="#000")
    await knowledge_service.add_tag(db_session, "note", both.id, tag_id=tag_x.id, name=None, color="#000")
    await knowledge_service.add_tag(db_session, "note", both.id, tag_id=tag_y.id, name=None, color="#000")

    items, total, _ = await knowledge_service.list_knowledge(db_session, tag_ids=[tag_x.id])
    assert {i.id for i in items} == {only_x.id, both.id}

    items, total, _ = await knowledge_service.list_knowledge(db_session, tag_ids=[tag_x.id, tag_y.id])
    assert total == 1
    assert items[0].id == both.id


async def test_list_knowledge_project_filter(db_session):
    scoped = await _make_note(db_session, title="scoped", project_id="proj-1")
    unscoped = await _make_note(db_session, title="unscoped")

    items, total, _ = await knowledge_service.list_knowledge(db_session, project_id="proj-1")
    assert total == 1
    assert items[0].id == scoped.id


# --- result cap (AC8a) -------------------------------------------------------


async def test_list_knowledge_caps_at_100_and_reports_truncation(db_session):
    import asyncio

    notes = []
    for i in range(105):
        notes.append(await _make_note(db_session, title=f"n{i}"))
        await asyncio.sleep(0.001)

    items, total, truncated = await knowledge_service.list_knowledge(db_session)
    assert len(items) == 100
    assert total == 105
    assert truncated is True
    # the 100 most recently updated - the 5 oldest (n0..n4) are excluded
    returned_titles = {i.title for i in items}
    for i in range(5):
        assert f"n{i}" not in returned_titles
    for i in range(5, 105):
        assert f"n{i}" in returned_titles


async def test_list_knowledge_exactly_100_is_not_truncated(db_session):
    for i in range(100):
        await _make_note(db_session, title=f"n{i}")

    items, total, truncated = await knowledge_service.list_knowledge(db_session)
    assert len(items) == 100
    assert total == 100
    assert truncated is False


async def test_list_knowledge_99_is_not_truncated(db_session):
    for i in range(99):
        await _make_note(db_session, title=f"n{i}")

    items, total, truncated = await knowledge_service.list_knowledge(db_session)
    assert len(items) == 99
    assert total == 99
    assert truncated is False


def test_list_knowledge_signature_has_no_pagination_parameter():
    params = set(inspect.signature(knowledge_service.list_knowledge).parameters)
    assert params == {"session", "q", "item_type", "tag_ids", "project_id"}
    for forbidden in ("limit", "page", "offset", "cursor"):
        assert forbidden not in params


# --- list_knowledge_tags -----------------------------------------------------


async def test_list_knowledge_tags_excludes_secret_only_tags(db_session):
    from app.models.secrets import Secret, SecretTagLink, SecretType

    used_tag = await _make_tag(db_session, "used")
    secret_only_tag = await _make_tag(db_session, "secret-only")

    note = await _make_note(db_session)
    await knowledge_service.add_tag(db_session, "note", note.id, tag_id=used_tag.id, name=None, color="#000")

    secret = Secret(name="s", type=SecretType.other, encrypted_value=b"x")
    db_session.add(secret)
    await db_session.commit()
    await db_session.refresh(secret)
    db_session.add(SecretTagLink(secret_id=secret.id, tag_id=secret_only_tag.id))
    await db_session.commit()

    pairs = await knowledge_service.list_knowledge_tags(db_session)
    names = {t.name: count for t, count in pairs}
    assert names == {"used": 1}


# --- tags (T5) ----------------------------------------------------------------


async def test_add_tag_by_new_name_creates_and_reuses(db_session):
    note = await _make_note(db_session)
    document = await _make_document(db_session)

    tags = await knowledge_service.add_tag(db_session, "note", note.id, tag_id=None, name="client-a", color="#111")
    assert [t.name for t in tags] == ["client-a"]

    tags2 = await knowledge_service.add_tag(db_session, "document", document.id, tag_id=None, name="client-a", color="#222")
    assert tags2[0].id == tags[0].id  # reused, not duplicated


async def test_add_tag_by_existing_id(db_session):
    tag = await _make_tag(db_session, "existing")
    note = await _make_note(db_session)
    tags = await knowledge_service.add_tag(db_session, "note", note.id, tag_id=tag.id, name=None, color="#000")
    assert tags[0].id == tag.id


async def test_remove_tag_unassigns_but_does_not_delete_tag_row(db_session):
    tag = await _make_tag(db_session, "keep-me")
    note = await _make_note(db_session)
    await knowledge_service.add_tag(db_session, "note", note.id, tag_id=tag.id, name=None, color="#000")

    await knowledge_service.remove_tag(db_session, "note", note.id, tag.id)

    tags = await knowledge_service._tags_for_item(db_session, "note", note.id)
    assert tags == []

    pairs = await knowledge_service.list_knowledge_tags(db_session)
    # tag row itself still exists (just unassigned everywhere)
    from sqlmodel import select

    result = await db_session.execute(select(Tag).where(Tag.id == tag.id))
    assert result.scalar_one_or_none() is not None


async def test_remove_tag_not_assigned_raises_not_found(db_session):
    tag = await _make_tag(db_session, "t")
    note = await _make_note(db_session)
    with pytest.raises(NotFoundError):
        await knowledge_service.remove_tag(db_session, "note", note.id, tag.id)


# --- links (T6) -----------------------------------------------------------


async def test_create_link_all_type_combinations(db_session):
    n1 = await _make_note(db_session)
    n2 = await _make_note(db_session)
    d1 = await _make_document(db_session)
    d2 = await _make_document(db_session)

    await knowledge_service.create_link(db_session, "note", n1.id, "note", n2.id)
    await knowledge_service.create_link(db_session, "note", n1.id, "document", d1.id)
    await knowledge_service.create_link(db_session, "document", d1.id, "document", d2.id)

    links = await knowledge_service.list_links(db_session, "note", n1.id)
    assert len(links) == 2


async def test_create_link_self_link_rejected(db_session):
    n1 = await _make_note(db_session)
    with pytest.raises(AppError) as exc:
        await knowledge_service.create_link(db_session, "note", n1.id, "note", n1.id)
    assert exc.value.code == "knowledge_link_self"


async def test_create_link_duplicate_rejected_in_either_direction(db_session):
    n1 = await _make_note(db_session)
    n2 = await _make_note(db_session)

    await knowledge_service.create_link(db_session, "note", n1.id, "note", n2.id)

    with pytest.raises(AppError) as exc:
        await knowledge_service.create_link(db_session, "note", n1.id, "note", n2.id)
    assert exc.value.code == "knowledge_link_duplicate"

    with pytest.raises(AppError) as exc:
        await knowledge_service.create_link(db_session, "note", n2.id, "note", n1.id)
    assert exc.value.code == "knowledge_link_duplicate"


async def test_list_links_oriented_from_both_sides(db_session):
    n1 = await _make_note(db_session, title="A")
    d1 = await _make_document(db_session, title="B")

    await knowledge_service.create_link(db_session, "note", n1.id, "document", d1.id)

    from_note = await knowledge_service.list_links(db_session, "note", n1.id)
    assert len(from_note) == 1
    assert from_note[0].other_type == "document"
    assert from_note[0].other_id == d1.id
    assert from_note[0].other_title == "B"

    from_doc = await knowledge_service.list_links(db_session, "document", d1.id)
    assert len(from_doc) == 1
    assert from_doc[0].other_type == "note"
    assert from_doc[0].other_id == n1.id
    assert from_doc[0].other_title == "A"


async def test_delete_link_removes_from_both_sides(db_session):
    n1 = await _make_note(db_session)
    n2 = await _make_note(db_session)
    link = await knowledge_service.create_link(db_session, "note", n1.id, "note", n2.id)

    await knowledge_service.delete_link(db_session, link.link_id)

    assert await knowledge_service.list_links(db_session, "note", n1.id) == []
    assert await knowledge_service.list_links(db_session, "note", n2.id) == []

    from sqlmodel import select

    from app.models.note import Note

    result = await db_session.execute(select(Note).where(Note.id.in_([n1.id, n2.id])))
    assert len(result.scalars().all()) == 2


async def test_purge_links_for_removes_orphans_from_either_side(db_session):
    n1 = await _make_note(db_session)
    n2 = await _make_note(db_session)
    n3 = await _make_note(db_session)

    await knowledge_service.create_link(db_session, "note", n1.id, "note", n2.id)
    await knowledge_service.create_link(db_session, "note", n3.id, "note", n1.id)

    await knowledge_service.purge_links_for(db_session, "note", n1.id)
    await db_session.commit()

    from sqlmodel import select

    from app.models.knowledge import KnowledgeLink

    result = await db_session.execute(
        select(KnowledgeLink).where(
            (KnowledgeLink.source_id == n1.id) | (KnowledgeLink.target_id == n1.id)
        )
    )
    assert result.scalars().all() == []
