from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.vault import SecretType


class SecretMetadata(BaseModel):
    username: str | None = None
    url: str | None = None
    notes: str | None = None


class FolderIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: str | None = None


class FolderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    parent_id: str | None
    created_at: datetime


class TagIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#6366f1", max_length=20)


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    color: str


class SecretCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: SecretType = SecretType.other
    value: str
    folder_id: str | None = None
    tag_ids: list[str] = Field(default_factory=list)
    metadata: SecretMetadata = Field(default_factory=SecretMetadata)
    favorite: bool = False


class SecretUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    type: SecretType | None = None
    value: str | None = None
    folder_id: str | None = None
    tag_ids: list[str] | None = None
    metadata: SecretMetadata | None = None
    favorite: bool | None = None


class SecretSummaryOut(BaseModel):
    id: str
    name: str
    type: SecretType
    folder_id: str | None
    tags: list[TagOut]
    favorite: bool
    created_at: datetime
    updated_at: datetime


class SecretDetailOut(SecretSummaryOut):
    value: str | None = None
    metadata: SecretMetadata


class SecretVersionOut(BaseModel):
    id: str
    created_at: datetime


class SecretVersionValueOut(BaseModel):
    id: str
    value: str
    created_at: datetime
