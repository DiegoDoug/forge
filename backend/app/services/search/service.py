from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.documents import service as documents_service
from app.services.notes import service as notes_service
from app.services.vault import service as vault_service


async def global_search(session: AsyncSession, query: str) -> dict:
    query = query.strip()
    if not query:
        return {"secrets": [], "notes": [], "documents": []}

    secrets = await vault_service.list_secrets(session, query=query)
    notes = await notes_service.search_notes(session, query)
    documents = await documents_service.search_documents(session, query)

    return {
        "secrets": [
            {"id": s.id, "name": s.name, "type": s.type, "folder_id": s.folder_id} for s in secrets[:10]
        ],
        "notes": [
            {"id": n.id, "title": n.title or "Untitled", "excerpt": n.content[:140]} for n in notes[:10]
        ],
        "documents": [
            {"id": d.id, "title": d.title or "Untitled"} for d in documents[:10]
        ],
    }
