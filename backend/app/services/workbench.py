from __future__ import annotations

import json
import shutil

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.version import VERSION
from app.models.activity import ActivityLog
from app.models.base import utcnow
from app.models.note import Note
from app.models.workbench import WorkbenchLayout

# Forward-looking tools carry "available": False until their own phase ships;
# they can still be pinned (rendered as "coming soon"), per 03_BACKEND.md §3.
WORKBENCH_TOOL_KEYS: dict[str, dict[str, bool]] = {
    "secrets": {"available": True},
    "notes": {"available": True},
    "documents": {"available": True},
    "generators": {"available": True},
    "crypto": {"available": True},
    "converters": {"available": True},
    "utilities": {"available": True},
    "ingest": {"available": True},
    "search": {"available": True},
    "prompt_studio": {"available": True},
    "universal_converter": {"available": False},
}

DEFAULT_LAYOUT_PANELS: list[dict[str, object]] = [
    {"type": "pinned_tools", "visible": True},
    {"type": "recent_activity", "visible": True},
    {"type": "quick_actions", "visible": True},
    {"type": "system_status", "visible": True},
    {"type": "recent_notes", "visible": True},
]

DEFAULT_PINNED_TOOLS: list[str] = ["ingest", "notes", "prompt_studio", "universal_converter", "secrets", "search"]


def _validate_panels(panels: list[dict]) -> None:
    seen: set[str] = set()
    for entry in panels:
        panel_type = entry.get("type") if isinstance(entry, dict) else None
        visible = entry.get("visible") if isinstance(entry, dict) else None
        if not isinstance(panel_type, str) or not panel_type:
            raise AppError(
                "Each panel entry must have a non-empty 'type'",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="validation_error",
            )
        if not isinstance(visible, bool):
            raise AppError(
                "Each panel entry must have a boolean 'visible'",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="validation_error",
            )
        if panel_type in seen:
            raise AppError(
                f"Duplicate panel type: {panel_type}",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="validation_error",
            )
        seen.add(panel_type)


def _validate_pinned_tools(pinned_tools: list[str]) -> None:
    for key in pinned_tools:
        if key not in WORKBENCH_TOOL_KEYS:
            raise AppError(
                f"Unknown pinned tool: {key}",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="validation_error",
            )


async def get_layout(session: AsyncSession) -> WorkbenchLayout:
    result = await session.execute(select(WorkbenchLayout).where(WorkbenchLayout.id == 1))
    layout = result.scalar_one_or_none()
    if layout is None:
        layout = WorkbenchLayout(
            id=1,
            panels=json.dumps(DEFAULT_LAYOUT_PANELS),
            pinned_tools=json.dumps(DEFAULT_PINNED_TOOLS),
        )
        session.add(layout)
        await session.commit()
        await session.refresh(layout)
    return layout


async def update_layout(session: AsyncSession, panels: list[dict], pinned_tools: list[str]) -> WorkbenchLayout:
    _validate_panels(panels)
    _validate_pinned_tools(pinned_tools)
    layout = await get_layout(session)
    layout.panels = json.dumps(panels)
    layout.pinned_tools = json.dumps(pinned_tools)
    layout.updated_at = utcnow()
    session.add(layout)
    await session.commit()
    await session.refresh(layout)
    return layout


async def reset_layout(session: AsyncSession) -> WorkbenchLayout:
    layout = await get_layout(session)
    layout.panels = json.dumps(DEFAULT_LAYOUT_PANELS)
    layout.pinned_tools = json.dumps(DEFAULT_PINNED_TOOLS)
    layout.updated_at = utcnow()
    session.add(layout)
    await session.commit()
    await session.refresh(layout)
    return layout


def serialize_layout(layout: WorkbenchLayout) -> dict:
    pinned_tool_keys: list[str] = json.loads(layout.pinned_tools)
    return {
        "panels": json.loads(layout.panels),
        "pinned_tools": [
            {"key": key, "available": WORKBENCH_TOOL_KEYS[key]["available"]} for key in pinned_tool_keys
        ],
        "tool_catalog": [{"key": key, "available": meta["available"]} for key, meta in WORKBENCH_TOOL_KEYS.items()],
    }


async def get_workbench(session: AsyncSession) -> dict:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(settings.data_dir)
    db_size = settings.database_path.stat().st_size if settings.database_path.exists() else 0

    activity_result = await session.execute(select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(15))
    notes_result = await session.execute(select(Note).where(Note.archived == False).order_by(Note.updated_at.desc()).limit(6))  # noqa: E712

    layout = await get_layout(session)

    return {
        "layout": serialize_layout(layout),
        "data": {
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
        },
    }
