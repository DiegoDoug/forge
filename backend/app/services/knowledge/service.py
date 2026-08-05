from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import AppError, NotFoundError
from app.models.document import Document
from app.models.knowledge import DocumentTagLink, KnowledgeLink, NoteTagLink
from app.models.note import Note
from app.models.secrets import Tag
from app.schemas.knowledge import KNOWLEDGE_RESULT_LIMIT
from app.services.documents import service as documents_service
from app.services.notes import service as notes_service

_EXCERPT_LENGTH = 140
_LINK_MODELS: dict[str, tuple[type, str]] = {
    "note": (NoteTagLink, "note_id"),
    "document": (DocumentTagLink, "document_id"),
}


@dataclass
class KnowledgeItem:
    type: str
    id: str
    title: str
    excerpt: str
    tags: list[Tag]
    project_id: str | None
    updated_at: datetime


@dataclass
class KnowledgeLinkView:
    link_id: str
    other_type: str
    other_id: str
    other_title: str
    created_at: datetime


def _link_model_for(item_type: str) -> tuple[type, str]:
    try:
        return _LINK_MODELS[item_type]
    except KeyError:
        raise AppError(f"Unknown item type: {item_type!r}", status_code=422, code="unknown_item_type") from None


async def _get_item_or_404(session: AsyncSession, item_type: str, item_id: str) -> None:
    if item_type == "note":
        result = await session.execute(select(Note.id).where(Note.id == item_id))
    elif item_type == "document":
        result = await session.execute(select(Document.id).where(Document.id == item_id))
    else:
        raise AppError(f"Unknown item type: {item_type!r}", status_code=422, code="unknown_item_type")
    if result.scalar_one_or_none() is None:
        raise NotFoundError(f"{item_type.capitalize()} not found")


async def _title_for(session: AsyncSession, item_type: str, item_id: str) -> str:
    column = Note.title if item_type == "note" else Document.title
    model = Note if item_type == "note" else Document
    result = await session.execute(select(column).where(model.id == item_id))
    title = result.scalar_one_or_none()
    return title or "Untitled"


# --- Query (T4) ----------------------------------------------------------


async def _candidate_notes(session: AsyncSession, q: str) -> list[Note]:
    if q.strip():
        # Delegates entirely to the existing FTS5-backed search - no MATCH
        # SQL of this module's own, per ADR-0015.
        return await notes_service.search_notes(session, q)
    result = await session.execute(select(Note).order_by(Note.updated_at.desc()))
    return list(result.scalars().all())


async def _candidate_documents(session: AsyncSession, q: str) -> list[Document]:
    if q.strip():
        return await documents_service.search_documents(session, q)
    result = await session.execute(select(Document).order_by(Document.updated_at.desc()))
    return list(result.scalars().all())


async def _tags_for(session: AsyncSession, item_type: str, item_ids: list[str]) -> dict[str, list[Tag]]:
    if not item_ids:
        return {}
    link_model, id_field = _link_model_for(item_type)
    result = await session.execute(
        select(getattr(link_model, id_field), Tag)
        .join(Tag, Tag.id == link_model.tag_id)
        .where(getattr(link_model, id_field).in_(item_ids))
    )
    out: dict[str, list[Tag]] = {item_id: [] for item_id in item_ids}
    for item_id, tag in result.all():
        out[item_id].append(tag)
    return out


async def list_knowledge(
    session: AsyncSession,
    *,
    q: str = "",
    item_type: str = "all",
    tag_ids: list[str] | None = None,
    project_id: str | None = None,
) -> tuple[list[KnowledgeItem], int, bool]:
    """The Hub query (01_SPEC.md FR1-FR6). No `limit` parameter - the
    fixed KNOWLEDGE_RESULT_LIMIT cap is applied after sorting by
    updated_at descending, so truncation always drops the oldest tail
    (01_SPEC.md SS6.6). Tag filtering is AND-only: an item must carry every
    id in tag_ids (SS6.8) - there is no OR mode."""
    tag_ids = tag_ids or []
    items: list[KnowledgeItem] = []

    if item_type in ("all", "note"):
        notes = await _candidate_notes(session, q)
        if project_id:
            notes = [n for n in notes if n.project_id == project_id]
        note_tags = await _tags_for(session, "note", [n.id for n in notes])
        for note in notes:
            tags = note_tags.get(note.id, [])
            if tag_ids and not set(tag_ids).issubset({t.id for t in tags}):
                continue
            items.append(
                KnowledgeItem(
                    type="note",
                    id=note.id,
                    title=note.title or "Untitled",
                    excerpt=note.content[:_EXCERPT_LENGTH],
                    tags=tags,
                    project_id=note.project_id,
                    updated_at=note.updated_at,
                )
            )

    if item_type in ("all", "document"):
        documents = await _candidate_documents(session, q)
        if project_id:
            documents = [d for d in documents if d.project_id == project_id]
        document_tags = await _tags_for(session, "document", [d.id for d in documents])
        for document in documents:
            tags = document_tags.get(document.id, [])
            if tag_ids and not set(tag_ids).issubset({t.id for t in tags}):
                continue
            items.append(
                KnowledgeItem(
                    type="document",
                    id=document.id,
                    title=document.title or "Untitled",
                    excerpt=document.content[:_EXCERPT_LENGTH],
                    tags=tags,
                    project_id=document.project_id,
                    updated_at=document.updated_at,
                )
            )

    items.sort(key=lambda item: item.updated_at, reverse=True)
    total = len(items)
    truncated = total > KNOWLEDGE_RESULT_LIMIT
    return items[:KNOWLEDGE_RESULT_LIMIT], total, truncated


async def list_knowledge_tags(session: AsyncSession) -> list[tuple[Tag, int]]:
    """Tags actually assigned to a Note or Document, with counts (FR12) - a
    tag used only by a Secret does not appear."""
    note_rows = await session.execute(select(NoteTagLink.tag_id))
    doc_rows = await session.execute(select(DocumentTagLink.tag_id))
    counts: dict[str, int] = {}
    for (tag_id,) in note_rows.all():
        counts[tag_id] = counts.get(tag_id, 0) + 1
    for (tag_id,) in doc_rows.all():
        counts[tag_id] = counts.get(tag_id, 0) + 1
    if not counts:
        return []
    result = await session.execute(select(Tag).where(Tag.id.in_(counts.keys())))
    tags = {t.id: t for t in result.scalars().all()}
    return [(tags[tid], count) for tid, count in counts.items() if tid in tags]


# --- Tags (T5) -------------------------------------------------------------


async def _get_tag_or_404(session: AsyncSession, tag_id: str) -> Tag:
    result = await session.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise NotFoundError("Tag not found")
    return tag


async def _get_or_create_tag_by_name(session: AsyncSession, name: str, color: str) -> Tag:
    result = await session.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if tag is not None:
        return tag
    tag = Tag(name=name, color=color)
    session.add(tag)
    await session.flush()
    return tag


async def add_tag(session: AsyncSession, item_type: str, item_id: str, *, tag_id: str | None, name: str | None, color: str) -> list[Tag]:
    """Assigns an existing tag by id, or creates-and-reuses one by name
    (FR10). Never creates a duplicate tags row for an existing name."""
    await _get_item_or_404(session, item_type, item_id)
    tag = await _get_tag_or_404(session, tag_id) if tag_id is not None else await _get_or_create_tag_by_name(session, name, color)

    link_model, id_field = _link_model_for(item_type)
    existing = await session.execute(
        select(link_model).where(getattr(link_model, id_field) == item_id, link_model.tag_id == tag.id)
    )
    if existing.scalar_one_or_none() is None:
        session.add(link_model(**{id_field: item_id, "tag_id": tag.id}))
        await session.commit()
    else:
        await session.commit()

    return await _tags_for_item(session, item_type, item_id)


async def remove_tag(session: AsyncSession, item_type: str, item_id: str, tag_id: str) -> None:
    """Unassigns only - never deletes the Tag row itself (FR11), since it
    may be in use elsewhere, including by Secrets."""
    await _get_item_or_404(session, item_type, item_id)
    link_model, id_field = _link_model_for(item_type)
    result = await session.execute(
        select(link_model).where(getattr(link_model, id_field) == item_id, link_model.tag_id == tag_id)
    )
    link = result.scalar_one_or_none()
    if link is None:
        raise NotFoundError("Tag is not assigned to this item")
    await session.delete(link)
    await session.commit()


async def _tags_for_item(session: AsyncSession, item_type: str, item_id: str) -> list[Tag]:
    link_model, id_field = _link_model_for(item_type)
    result = await session.execute(
        select(Tag).join(link_model, link_model.tag_id == Tag.id).where(getattr(link_model, id_field) == item_id)
    )
    return list(result.scalars().all())


# --- Links (T6) ------------------------------------------------------------


def _normalize_pair(source_type: str, source_id: str, target_type: str, target_id: str) -> tuple[str, str, str, str]:
    """Orders the pair so A-to-B and B-to-A always store as the same row
    (01_SPEC.md FR18) - the unique constraint on knowledge_links holds
    against these normalized columns."""
    a, b = (source_type, source_id), (target_type, target_id)
    return (*a, *b) if a <= b else (*b, *a)


async def create_link(
    session: AsyncSession, source_type: str, source_id: str, target_type: str, target_id: str
) -> KnowledgeLinkView:
    """Returns a view oriented relative to (source_type, source_id) - the
    item the caller linked *from* - matching list_links' shape (06_API.md
    SS1.4), so the route layer never touches the raw ORM row or any
    private helper."""
    await _get_item_or_404(session, source_type, source_id)
    await _get_item_or_404(session, target_type, target_id)

    if source_type == target_type and source_id == target_id:
        raise AppError("An item cannot be linked to itself", status_code=400, code="knowledge_link_self")

    s_type, s_id, t_type, t_id = _normalize_pair(source_type, source_id, target_type, target_id)
    existing = await session.execute(
        select(KnowledgeLink).where(
            KnowledgeLink.source_type == s_type,
            KnowledgeLink.source_id == s_id,
            KnowledgeLink.target_type == t_type,
            KnowledgeLink.target_id == t_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise AppError("This link already exists", status_code=409, code="knowledge_link_duplicate")

    link = KnowledgeLink(source_type=s_type, source_id=s_id, target_type=t_type, target_id=t_id)
    session.add(link)
    await session.commit()
    await session.refresh(link)

    title = await _title_for(session, target_type, target_id)
    return KnowledgeLinkView(link_id=link.id, other_type=target_type, other_id=target_id, other_title=title, created_at=link.created_at)


async def list_links(session: AsyncSession, item_type: str, item_id: str) -> list[KnowledgeLinkView]:
    """Links from both sides, each oriented relative to (item_type, item_id)
    so the caller never has to work out which end it is on (06_API.md SS1.4)."""
    await _get_item_or_404(session, item_type, item_id)
    result = await session.execute(
        select(KnowledgeLink).where(
            ((KnowledgeLink.source_type == item_type) & (KnowledgeLink.source_id == item_id))
            | ((KnowledgeLink.target_type == item_type) & (KnowledgeLink.target_id == item_id))
        )
    )
    views: list[KnowledgeLinkView] = []
    for link in result.scalars().all():
        if link.source_type == item_type and link.source_id == item_id:
            other_type, other_id = link.target_type, link.target_id
        else:
            other_type, other_id = link.source_type, link.source_id
        title = await _title_for(session, other_type, other_id)
        views.append(
            KnowledgeLinkView(
                link_id=link.id, other_type=other_type, other_id=other_id, other_title=title, created_at=link.created_at
            )
        )
    return views


async def delete_link(session: AsyncSession, link_id: str) -> None:
    result = await session.execute(select(KnowledgeLink).where(KnowledgeLink.id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise NotFoundError("Link not found")
    await session.delete(link)
    await session.commit()


async def purge_links_for(session: AsyncSession, item_type: str, item_id: str) -> None:
    """Deletes every knowledge_links row referencing (item_type, item_id)
    from either side (FR17) - service-enforced because knowledge_links is
    polymorphic and cannot carry a real FK (04_DATABASE.md SS2). Does not
    commit: called from the route layer immediately before the owning
    delete_note/delete_document call, per the T6/03_BACKEND.md SS2.2
    delete-hook decision below.

    Delete-hook direction decided: routes call this, not
    services/notes/documents. The alternative (notes/service.py and
    documents/service.py calling into services/knowledge/service.py
    directly) would create a circular import - this module already imports
    notes_service/documents_service at module level to delegate FTS search
    (SS Query above), so the reverse import cannot also exist at module
    level. Routing the hook through api/routes/notes.py and
    api/routes/documents.py (T7) instead keeps both feature services free
    of any knowledge-module dependency, which is also the narrower,
    safer choice per 03_BACKEND.md SS2.2's own fallback.
    """
    result = await session.execute(
        select(KnowledgeLink).where(
            ((KnowledgeLink.source_type == item_type) & (KnowledgeLink.source_id == item_id))
            | ((KnowledgeLink.target_type == item_type) & (KnowledgeLink.target_id == item_id))
        )
    )
    for link in result.scalars().all():
        await session.delete(link)
