from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import utcnow


class AppConfig(SQLModel, table=True):
    """Single-row table (id is always 1) holding instance-wide settings."""

    __tablename__ = "app_config"

    id: int = Field(default=1, primary_key=True)
    master_password_hash: str | None = Field(default=None)
    theme: str = Field(default="dark", max_length=20)
    setup_completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
