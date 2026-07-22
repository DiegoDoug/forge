from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import new_id, utcnow


class ProjectInitGeneration(SQLModel, table=True):
    """History record for a Project Init generation. Stores the validated
    input config, not the rendered files - output is deterministically
    re-rendered from (kind, config) on every download, same pattern as
    services/documents/export.py's export-on-demand."""

    __tablename__ = "project_init_generations"

    id: str = Field(default_factory=new_id, primary_key=True)
    kind: str = Field(max_length=32, index=True)
    name: str = Field(max_length=120)
    config: str = Field(default="{}")  # JSON-encoded GenerateRequest.config
    created_at: datetime = Field(default_factory=utcnow, index=True)
