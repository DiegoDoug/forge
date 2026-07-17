from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreateIn(BaseModel):
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")
    pinned: bool = False


class DocumentUpdateIn(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    pinned: bool | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    pinned: bool
    created_at: datetime
    updated_at: datetime


class DocumentSummaryOut(BaseModel):
    """Lighter shape for the history sidebar list — omits ``content`` so
    scrolling a long document history doesn't ship every document's full
    HTML body on every page load."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    pinned: bool
    created_at: datetime
    updated_at: datetime
