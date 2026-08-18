from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from .base import new_id, utcnow


class ActivityAction(str, Enum):
    created = "created"
    updated = "updated"
    deleted = "deleted"
    viewed = "viewed"
    converted = "converted"


class ActivityLog(SQLModel, table=True):
    """Lightweight feed used by the Workbench's Recent Activity panel.
    Never stores secret values or converted document contents."""

    __tablename__ = "activity_log"

    id: str = Field(default_factory=new_id, primary_key=True)
    action: ActivityAction
    entity_type: str = Field(max_length=50, index=True)
    entity_id: str = Field(max_length=64)
    summary: str = Field(max_length=300)
    created_at: datetime = Field(default_factory=utcnow, index=True)
    # "ui" (default, every existing call site) vs "mcp" (Phase 11 MCP-originated
    # writes). Added in Milestone 1 as a column only - no service function
    # threads a non-default value through yet, since Milestone 1 registers zero
    # MCP write tools. Wiring `source="mcp"` through notes/documents/projects
    # services is Milestone 2 scope (01_SPEC.md SS4.5, 09_IMPLEMENTATION_TASKS.md
    # M2-T0) - deliberately not done here to keep this milestone's diff to
    # exactly what M1-T2 specifies.
    source: str = Field(default="ui", max_length=20)
