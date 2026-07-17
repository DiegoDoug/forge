from __future__ import annotations

import shutil

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import get_settings
from app.core.version import VERSION
from app.models.activity import ActivityLog
from app.models.note import Note
from app.services.vault import service as vault_service


async def get_dashboard(session: AsyncSession) -> dict:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(settings.data_dir)
    db_size = settings.database_path.stat().st_size if settings.database_path.exists() else 0

    activity_result = await session.execute(select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(15))
    notes_result = await session.execute(select(Note).where(Note.archived == False).order_by(Note.updated_at.desc()).limit(6))  # noqa: E712
    secrets = (await vault_service.list_secrets(session))[:6]

    return {
        "version": VERSION,
        "storage": {
            "database_bytes": db_size,
            "disk_total_bytes": usage.total,
            "disk_used_bytes": usage.used,
            "disk_free_bytes": usage.free,
        },
        "recent_activity": [
            {
                "id": a.id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "summary": a.summary,
                "created_at": a.created_at,
            }
            for a in activity_result.scalars().all()
        ],
        "recent_notes": [
            {"id": n.id, "title": n.title or "Untitled", "color": n.color, "updated_at": n.updated_at}
            for n in notes_result.scalars().all()
        ],
        "recent_secrets": [
            {"id": s.id, "name": s.name, "type": s.type, "updated_at": s.updated_at} for s in secrets
        ],
    }
