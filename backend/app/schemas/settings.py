from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ThemeIn(BaseModel):
    theme: str


class AboutOut(BaseModel):
    name: str
    version: str
    environment: str


class BackupOut(BaseModel):
    version: int
    exported_at: str
    folders: list[dict[str, Any]]
    tags: list[dict[str, Any]]
    secrets: list[dict[str, Any]]
    notes: list[dict[str, Any]]


class BackupImportIn(BaseModel):
    version: int
    folders: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
