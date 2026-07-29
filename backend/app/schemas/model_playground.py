from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.services.model_playground.providers import PROVIDER_REGISTRY

MAX_TARGETS_PER_RUN = 6
PROMPT_EXCERPT_LENGTH = 120


def _check_provider(provider: str) -> str:
    if provider not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider '{provider}'")
    return provider


class ProviderAvailability(BaseModel):
    provider: str
    display_name: str
    configured: bool
    models: list[str]


class ProviderCredentialIn(BaseModel):
    provider: str
    label: str | None = Field(default=None, max_length=200)
    api_key: str = Field(min_length=1, max_length=2000)

    @field_validator("provider")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return _check_provider(v)


class ProviderCredentialOut(BaseModel):
    id: str
    provider: str
    label: str
    created_at: datetime
    updated_at: datetime


class ProviderCredentialListOut(BaseModel):
    items: list[ProviderCredentialOut]


class RunTargetIn(BaseModel):
    provider: str
    model: str

    @field_validator("provider")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return _check_provider(v)

    @model_validator(mode="after")
    def _validate_model(self) -> "RunTargetIn":
        spec = PROVIDER_REGISTRY[self.provider]
        if self.model not in spec.models:
            raise ValueError(f"Model '{self.model}' is not supported for provider '{self.provider}'")
        return self


class PlaygroundRunIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)
    targets: list[RunTargetIn] = Field(min_length=1, max_length=MAX_TARGETS_PER_RUN)

    @field_validator("targets")
    @classmethod
    def _validate_unique_targets(cls, v: list[RunTargetIn]) -> list[RunTargetIn]:
        seen = {(t.provider, t.model) for t in v}
        if len(seen) != len(v):
            raise ValueError("Duplicate provider/model targets are not allowed in a single run")
        return v


class PlaygroundResultOut(BaseModel):
    id: str
    provider: str
    model: str
    status: Literal["success", "error", "timeout"]
    response_text: str | None
    error_message: str | None
    latency_ms: int | None
    prompt_tokens: int | None
    completion_tokens: int | None


class PlaygroundRunOut(BaseModel):
    id: str
    prompt: str
    created_at: datetime
    results: list[PlaygroundResultOut]


class PlaygroundRunListItemOut(BaseModel):
    id: str
    prompt_excerpt: str
    providers: list[str]
    created_at: datetime


class PlaygroundRunListOut(BaseModel):
    items: list[PlaygroundRunListItemOut]
