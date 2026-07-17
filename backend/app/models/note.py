from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import new_id, utcnow


class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: str = Field(default_factory=new_id, primary_key=True)
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")  # markdown
    color: str = Field(default="#fde68a", max_length=20)

    pos_x: float = Field(default=0)
    pos_y: float = Field(default=0)
    width: float = Field(default=280)
    height: float = Field(default=220)
    z_index: int = Field(default=0)

    pinned: bool = Field(default=False, index=True)
    archived: bool = Field(default=False, index=True)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow, index=True)
