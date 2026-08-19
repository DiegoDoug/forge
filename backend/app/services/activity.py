from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityAction, ActivityLog


def record(
    session: AsyncSession,
    action: ActivityAction,
    entity_type: str,
    entity_id: str,
    summary: str,
    *,
    source: str = "ui",
) -> None:
    """Queues an activity row on the given session; caller commits.

    ``source`` distinguishes MCP-originated writes (Phase 11) from
    UI-originated ones - defaults to "ui" so every pre-existing call site is
    unaffected; only MCP tool handlers pass ``source="mcp"`` explicitly."""
    session.add(
        ActivityLog(action=action, entity_type=entity_type, entity_id=entity_id, summary=summary[:300], source=source)
    )
