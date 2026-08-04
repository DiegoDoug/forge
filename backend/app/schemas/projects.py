from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Reuses Model Playground's own provider/model membership checks (Phase 05)
# so the two can never drift - Projects never re-implements provider
# validation, per ADR-0014 SS2.
from app.schemas.model_playground import _check_model, _check_provider

PROMPT_MAX_LENGTH = 20000


class ProjectCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    color: str = Field(default="#6366f1", max_length=20)
    default_provider: str | None = None
    default_model: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def _validate_provider_model_pair(self) -> "ProjectCreateIn":
        _validate_default_ai(self.default_provider, self.default_model)
        return self


class ProjectUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, max_length=20)
    archived: bool | None = None
    default_provider: str | None = None
    default_model: str | None = Field(default=None, max_length=100)
    clear_default_ai: bool = Field(
        default=False,
        description="If true, clears default_provider/default_model regardless of the two fields above.",
    )

    @model_validator(mode="after")
    def _validate_provider_model_pair(self) -> "ProjectUpdateIn":
        if not self.clear_default_ai and (self.default_provider is not None or self.default_model is not None):
            _validate_default_ai(self.default_provider, self.default_model)
        return self


def _validate_default_ai(provider: str | None, model: str | None) -> None:
    if (provider is None) != (model is None):
        raise ValueError("default_provider and default_model must be set together, or both left unset")
    if provider is not None and model is not None:
        _check_provider(provider)
        _check_model(provider, model)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    color: str
    archived: bool
    default_provider: str | None
    default_model: str | None
    secret_count: int
    note_count: int
    document_count: int
    created_at: datetime
    updated_at: datetime


class ProjectSummaryOut(BaseModel):
    id: str
    name: str
    color: str
    archived: bool
    secret_count: int
    note_count: int
    document_count: int
    updated_at: datetime


class ProjectAiRunIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=PROMPT_MAX_LENGTH)
