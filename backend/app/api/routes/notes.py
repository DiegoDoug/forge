from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.schemas.notes import NoteCreateIn, NoteOut, NoteUpdateIn
from app.services.knowledge import service as knowledge_service
from app.services.notes import service

router = APIRouter(prefix="/notes", tags=["notes"], dependencies=[AuthDep])


@router.get("", response_model=list[NoteOut])
async def list_notes(session: SessionDep, archived: bool = False, project_id: str | None = None) -> list[NoteOut]:
    return list(await service.list_notes(session, archived=archived, project_id=project_id))


@router.get("/search", response_model=list[NoteOut])
async def search_notes(session: SessionDep, q: str) -> list[NoteOut]:
    return list(await service.search_notes(session, q))


@router.post("", response_model=NoteOut, status_code=201)
async def create_note(body: NoteCreateIn, session: SessionDep) -> NoteOut:
    return await service.create_note(session, body)


@router.patch("/{note_id}", response_model=NoteOut)
async def update_note(note_id: str, body: NoteUpdateIn, session: SessionDep) -> NoteOut:
    return await service.update_note(session, note_id, body)


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: str, session: SessionDep) -> None:
    # Delete-hook direction (03_BACKEND.md SS2.2, decided at T6): the route
    # layer purges knowledge_links before deleting, rather than
    # services/notes/service.py importing services/knowledge/service.py -
    # that would be a circular import, since knowledge/service.py already
    # imports notes/service.py at module level to delegate FTS search.
    await knowledge_service.purge_links_for(session, "note", note_id)
    await service.delete_note(session, note_id)
