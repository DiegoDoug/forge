from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityAction, ActivityLog


def record(session: AsyncSession, action: ActivityAction, entity_type: str, entity_id: str, summary: str) -> None:
    """Queues an activity row on the given session; caller commits."""
    session.add(ActivityLog(action=action, entity_type=entity_type, entity_id=entity_id, summary=summary[:300]))
