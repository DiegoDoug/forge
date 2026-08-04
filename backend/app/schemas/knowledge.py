from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator

from app.schemas.secrets import TagOut

KNOWLEDGE_RESULT_LIMIT = 100
"""Fixed server-side cap on GET /api/knowledge results - not caller-
configurable. There is no page/offset/cursor/limit parameter anywhere in
this phase; see 01_SPEC.md SS6.6/SS6.7 and 06_API.md SS1.1a."""


class KnowledgeItemType(str, Enum):
    note = "note"
    document = "document"


class KnowledgeItemOut(BaseModel):
    type: KnowledgeItemType
    id: str
    title: str
    excerpt: str
    tags: list[TagOut]
    project_id: str | None
    updated_at: datetime


class KnowledgeListOut(BaseModel):
    items: list[KnowledgeItemOut]
    total: int
    truncated: bool


class KnowledgeTagOut(BaseModel):
    id: str
    name: str
    color: str
    count: int


class KnowledgeTagAssignIn(BaseModel):
    tag_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str = Field(default="#6366f1", max_length=20)

    @model_validator(mode="after")
    def _exactly_one_of_tag_id_or_name(self) -> "KnowledgeTagAssignIn":
        if (self.tag_id is None) == (self.name is None):
            raise ValueError("exactly one of tag_id or name must be provided")
        return self


class KnowledgeLinkCreateIn(BaseModel):
    target_type: KnowledgeItemType
    target_id: str


class KnowledgeLinkOtherOut(BaseModel):
    type: KnowledgeItemType
    id: str
    title: str


class KnowledgeLinkOut(BaseModel):
    link_id: str
    other: KnowledgeLinkOtherOut
    created_at: datetime
