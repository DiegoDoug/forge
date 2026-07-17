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
    """Lightweight feed used by the dashboard's "Recent activity" widget.
    Never stores secret values or converted document contents."""

    __tablename__ = "activity_log"

    id: str = Field(default_factory=new_id, primary_key=True)
    action: ActivityAction
    entity_type: str = Field(max_length=50, index=True)
    entity_id: str = Field(max_length=64)
    summary: str = Field(max_length=300)
    created_at: datetime = Field(default_factory=utcnow, index=True)
