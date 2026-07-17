from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreateIn(BaseModel):
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")
    color: str = Field(default="#fde68a", max_length=20)
    pos_x: float = 0
    pos_y: float = 0
    width: float = 280
    height: float = 220


class NoteUpdateIn(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    color: str | None = Field(default=None, max_length=20)
    pos_x: float | None = None
    pos_y: float | None = None
    width: float | None = None
    height: float | None = None
    z_index: int | None = None
    pinned: bool | None = None
    archived: bool | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    color: str
    pos_x: float
    pos_y: float
    width: float
    height: float
    z_index: int
    pinned: bool
    archived: bool
    created_at: datetime
    updated_at: datetime
