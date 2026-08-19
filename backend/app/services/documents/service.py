from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import NotFoundError
from app.models.activity import ActivityAction
from app.models.base import utcnow
from app.models.document import Document
from app.services import activity


async def _get_or_404(session: AsyncSession, document_id: str) -> Document:
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise NotFoundError("Document not found")
    return document


async def list_documents(session: AsyncSession, *, project_id: str | None = None) -> list[Document]:
    stmt = select(Document)
    if project_id:
        stmt = stmt.where(Document.project_id == project_id)
    result = await session.execute(stmt.order_by(Document.pinned.desc(), Document.updated_at.desc()))
    return list(result.scalars().all())


async def search_documents(session: AsyncSession, query: str, *, project_id: str | None = None) -> list[Document]:
    """FTS5 full-text search over document title/content, mirroring the
    notes search implementation. ``project_id`` is query-scoped, not a
    post-filter - see notes_service.search_notes's identical note
    (01_SPEC.md SS5.2, Phase 11 M3-T0a)."""
    if not query.strip():
        return []
    sql = (
        "SELECT documents.* FROM documents "
        "JOIN documents_fts ON documents.rowid = documents_fts.rowid "
        "WHERE documents_fts MATCH :query"
    )
    params: dict[str, str] = {"query": f'"{query}"*'}
    if project_id is not None:
        sql += " AND documents.project_id = :project_id"
        params["project_id"] = project_id
    sql += " ORDER BY rank LIMIT 50"
    rows = await session.execute(text(sql), params)
    ids = [row.id for row in rows]
    if not ids:
        return []
    result = await session.execute(select(Document).where(Document.id.in_(ids)))
    by_id = {d.id: d for d in result.scalars().all()}
    return [by_id[i] for i in ids if i in by_id]


async def get_document(session: AsyncSession, document_id: str) -> Document:
    return await _get_or_404(session, document_id)


async def create_document(session: AsyncSession, data, *, source: str = "ui") -> Document:
    document = Document(**data.model_dump())
    session.add(document)
    activity.record(
        session,
        ActivityAction.created,
        "document",
        document.id,
        f'Created document "{document.title or "Untitled"}"',
        source=source,
    )
    await session.commit()
    await session.refresh(document)
    return document


async def update_document(session: AsyncSession, document_id: str, data) -> Document:
    # No activity.record call - matches this function's existing behavior
    # exactly (only create_document/delete_document log for Documents today).
    # See notes/service.py::update_note's identical note for the full
    # reasoning - out of Milestone 2's scope to add new logging behavior to
    # an existing REST-facing update path.
    document = await _get_or_404(session, document_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    document.updated_at = utcnow()
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def delete_document(session: AsyncSession, document_id: str, *, source: str = "ui") -> None:
    document = await _get_or_404(session, document_id)
    title = document.title or "Untitled"
    await session.delete(document)
    activity.record(
        session, ActivityAction.deleted, "document", document_id, f'Deleted document "{title}"', source=source
    )
    await session.commit()
