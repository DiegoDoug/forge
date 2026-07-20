from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import utcnow


class WorkbenchLayout(SQLModel, table=True):
    """Single-row table (id is always 1) holding the instance-wide Workbench layout."""

    __tablename__ = "workbench_layout"

    id: int = Field(default=1, primary_key=True)
    panels: str = Field(default="[]")  # JSON-encoded list[{"type": str, "visible": bool}], in display order
    pinned_tools: str = Field(default="[]")  # JSON-encoded list[str] of tool keys, in pin order
    updated_at: datetime = Field(default_factory=utcnow)
