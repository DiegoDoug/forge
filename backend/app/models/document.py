from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import new_id, utcnow


class Document(SQLModel, table=True):
    """A full document edited in the Documents tab. ``content`` is the
    editor's HTML, stored as plain text (no blob/binary column) so the
    export formats (txt/md/xml/doc/docx/pdf) are always derived on demand
    rather than duplicated at rest."""

    __tablename__ = "documents"

    id: str = Field(default_factory=new_id, primary_key=True)
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")  # editor HTML

    pinned: bool = Field(default=False, index=True)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow, index=True)
