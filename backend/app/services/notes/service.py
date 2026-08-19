from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import NotFoundError
from app.models.activity import ActivityAction
from app.models.base import utcnow
from app.models.note import Note
from app.services import activity


async def _get_or_404(session: AsyncSession, note_id: str) -> Note:
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if note is None:
        raise NotFoundError("Note not found")
    return note


async def list_notes(session: AsyncSession, *, archived: bool = False, project_id: str | None = None) -> list[Note]:
    stmt = select(Note).where(Note.archived == archived)
    if project_id:
        stmt = stmt.where(Note.project_id == project_id)
    result = await session.execute(stmt.order_by(Note.pinned.desc(), Note.updated_at.desc()))
    return list(result.scalars().all())


async def search_notes(session: AsyncSession, query: str) -> list[Note]:
    """FTS5 full-text search over note title/content, joined back to the
    live rows via SQLite's implicit rowid (the external-content FTS5 index
    is kept in sync by triggers created in the initial migration)."""
    if not query.strip():
        return []
    rows = await session.execute(
        text(
            "SELECT notes.* FROM notes "
            "JOIN notes_fts ON notes.rowid = notes_fts.rowid "
            "WHERE notes_fts MATCH :query ORDER BY rank LIMIT 50"
        ),
        {"query": f'"{query}"*'},
    )
    ids = [row.id for row in rows]
    if not ids:
        return []
    result = await session.execute(select(Note).where(Note.id.in_(ids)))
    by_id = {n.id: n for n in result.scalars().all()}
    return [by_id[i] for i in ids if i in by_id]


async def create_note(session: AsyncSession, data, *, source: str = "ui") -> Note:
    note = Note(**data.model_dump())
    session.add(note)
    activity.record(
        session, ActivityAction.created, "note", note.id, f'Created note "{note.title or "Untitled"}"', source=source
    )
    await session.commit()
    await session.refresh(note)
    return note


async def update_note(session: AsyncSession, note_id: str, data) -> Note:
    # No activity.record call here, matching this function's existing
    # behavior exactly (confirmed against the pre-Phase-11 baseline) - only
    # create_note/delete_note log to ActivityLog for Notes today. Adding
    # update-logging would be a new behavior change to the existing REST
    # PATCH /api/notes/{id} path too (every UI edit would start appearing in
    # Recent Activity when it doesn't today), not merely "threading a
    # parameter through" - out of Milestone 2's scope per IMPLEMENT.md's own
    # "any change to the audit-logging design is a new decision" rule. No
    # `source` param here for the same reason: there is nothing to thread it
    # into. forge_update_note (MCP) therefore produces no ActivityLog row,
    # exactly matching what a UI-driven note edit does today (08_ACCEPTANCE.md
    # AC6's "same ActivityLog pattern" is satisfied literally, not assumed).
    note = await _get_or_404(session, note_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    note.updated_at = utcnow()
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def delete_note(session: AsyncSession, note_id: str, *, source: str = "ui") -> None:
    note = await _get_or_404(session, note_id)
    title = note.title or "Untitled"
    await session.delete(note)
    activity.record(session, ActivityAction.deleted, "note", note_id, f'Deleted note "{title}"', source=source)
    await session.commit()


async def get_note(session: AsyncSession, note_id: str) -> Note:
    return await _get_or_404(session, note_id)
