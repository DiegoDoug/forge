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


async def list_documents(session: AsyncSession) -> list[Document]:
    result = await session.execute(select(Document).order_by(Document.pinned.desc(), Document.updated_at.desc()))
    return list(result.scalars().all())


async def search_documents(session: AsyncSession, query: str) -> list[Document]:
    """FTS5 full-text search over document title/content, mirroring the
    notes search implementation."""
    if not query.strip():
        return []
    rows = await session.execute(
        text(
            "SELECT documents.* FROM documents "
            "JOIN documents_fts ON documents.rowid = documents_fts.rowid "
            "WHERE documents_fts MATCH :query ORDER BY rank LIMIT 50"
        ),
        {"query": f'"{query}"*'},
    )
    ids = [row.id for row in rows]
    if not ids:
        return []
    result = await session.execute(select(Document).where(Document.id.in_(ids)))
    by_id = {d.id: d for d in result.scalars().all()}
    return [by_id[i] for i in ids if i in by_id]


async def get_document(session: AsyncSession, document_id: str) -> Document:
    return await _get_or_404(session, document_id)


async def create_document(session: AsyncSession, data) -> Document:
    document = Document(**data.model_dump())
    session.add(document)
    activity.record(
        session, ActivityAction.created, "document", document.id, f'Created document "{document.title or "Untitled"}"'
    )
    await session.commit()
    await session.refresh(document)
    return document


async def update_document(session: AsyncSession, document_id: str, data) -> Document:
    document = await _get_or_404(session, document_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    document.updated_at = utcnow()
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def delete_document(session: AsyncSession, document_id: str) -> None:
    document = await _get_or_404(session, document_id)
    title = document.title or "Untitled"
    await session.delete(document)
    activity.record(session, ActivityAction.deleted, "document", document_id, f'Deleted document "{title}"')
    await session.commit()
