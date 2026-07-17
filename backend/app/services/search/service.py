from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notes import service as notes_service
from app.services.vault import service as vault_service


async def global_search(session: AsyncSession, query: str) -> dict:
    query = query.strip()
    if not query:
        return {"secrets": [], "notes": []}

    secrets = await vault_service.list_secrets(session, query=query)
    notes = await notes_service.search_notes(session, query)

    return {
        "secrets": [
            {"id": s.id, "name": s.name, "type": s.type, "folder_id": s.folder_id} for s in secrets[:10]
        ],
        "notes": [
            {"id": n.id, "title": n.title or "Untitled", "excerpt": n.content[:140]} for n in notes[:10]
        ],
    }
