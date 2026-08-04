from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import new_id, utcnow


class Project(SQLModel, table=True):
    """A named workspace that Secrets, Notes, and Documents can optionally
    scope into (ADR-0014). ``default_provider``/``default_model`` are plain
    string references into model_playground's PROVIDER_REGISTRY - never a
    credential, never a foreign key to ProviderCredential (see ADR-0014 SS2
    and ADR-0011 SS2.4's precedent on PlaygroundResult)."""

    __tablename__ = "projects"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(index=True, max_length=200)
    description: str = Field(default="", max_length=2000)
    color: str = Field(default="#6366f1", max_length=20)
    archived: bool = Field(default=False, index=True)

    default_provider: str | None = Field(default=None, max_length=50)
    default_model: str | None = Field(default=None, max_length=100)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
