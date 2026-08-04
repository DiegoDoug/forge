from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, Index, SQLModel, UniqueConstraint

from .base import new_id, utcnow


class NoteTagLink(SQLModel, table=True):
    """Mirrors ``SecretTagLink`` (models/secrets.py) exactly, against the
    same shared ``tags`` table, per ADR-0015 / 01_SPEC.md SS6.3."""

    __tablename__ = "note_tag_links"

    note_id: str = Field(foreign_key="notes.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)


class DocumentTagLink(SQLModel, table=True):
    __tablename__ = "document_tag_links"

    document_id: str = Field(foreign_key="documents.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)


class KnowledgeLink(SQLModel, table=True):
    """An explicit, undirected-in-product link between two knowledge items
    (note or document, in any combination). Polymorphic by design
    (``source_type``/``target_type``), so SQLite cannot enforce a foreign
    key on ``source_id``/``target_id`` - orphan prevention on delete is
    service-enforced (``purge_links_for``), not a DB guarantee. See
    04_DATABASE.md SS2 and 01_SPEC.md SS6.5 for the full rationale.

    The service layer normalizes each pair (ordering by (type, id)) before
    insert, so A-to-B and B-to-A are always stored as the same row; the
    unique constraint below then holds against the normalized columns.
    """

    __tablename__ = "knowledge_links"
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", "target_type", "target_id", name="uq_knowledge_links_pair"),
        Index("ix_knowledge_links_source", "source_type", "source_id"),
        Index("ix_knowledge_links_target", "target_type", "target_id"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    source_type: str = Field(max_length=10)
    source_id: str = Field(max_length=64)
    target_type: str = Field(max_length=10)
    target_id: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=utcnow)
