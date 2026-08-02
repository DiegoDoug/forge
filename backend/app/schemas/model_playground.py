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


def _check_base_url(v: str) -> str:
    # Well-formed http(s) only - rejects `file://` and other schemes a
    # misconfigured client library might otherwise follow. Deliberately not
    # an allowlist of hosts/IP ranges - see ADR-0013 SS4 for why (this is a
    # single-trusted-operator instance, and pointing at a local/self-hosted
    # OpenAI-compatible server is a legitimate, intended use case).
    if not (v.startswith("http://") or v.startswith("https://")):
        raise ValueError("base_url must start with http:// or https://")
    return v


def _check_model(provider: str, model: str) -> str:
    spec = PROVIDER_REGISTRY[provider]
    if not spec.allows_custom_model and model not in spec.models:
        raise ValueError(f"Model '{model}' is not supported for provider '{provider}'")
    return model


class ProviderAvailability(BaseModel):
    provider: str
    display_name: str
    configured: bool
    models: list[str]
    requires_base_url: bool
    allows_custom_model: bool


class ProviderCredentialIn(BaseModel):
    provider: str
    label: str | None = Field(default=None, max_length=200)
    api_key: str = Field(min_length=1, max_length=2000)
    base_url: str | None = Field(default=None, min_length=1, max_length=500)

    @field_validator("provider")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return _check_provider(v)

    @field_validator("base_url")
    @classmethod
    def _validate_base_url_scheme(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _check_base_url(v)

    @model_validator(mode="after")
    def _validate_base_url_required_or_forbidden(self) -> "ProviderCredentialIn":
        spec = PROVIDER_REGISTRY[self.provider]
        if spec.requires_base_url and not self.base_url:
            raise ValueError(f"Provider '{self.provider}' requires a base_url")
        if not spec.requires_base_url and self.base_url:
            raise ValueError(f"Provider '{self.provider}' does not accept a base_url")
        return self


class ProviderCredentialOut(BaseModel):
    id: str
    provider: str
    label: str
    base_url: str | None
    created_at: datetime
    updated_at: datetime


class ProviderCredentialListOut(BaseModel):
    items: list[ProviderCredentialOut]


class RunTargetIn(BaseModel):
    provider: str
    model: str = Field(min_length=1, max_length=100)

    @field_validator("provider")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return _check_provider(v)

    @model_validator(mode="after")
    def _validate_model(self) -> "RunTargetIn":
        # Custom (and any future allows_custom_model provider) has no fixed
        # catalogue to validate against - Forge can't know it ahead of time
        # (ADR-0013 SS2.3). Every other provider keeps the existing
        # membership check.
        _check_model(self.provider, self.model)
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


class ProviderConnectionTestIn(BaseModel):
    """Stateless connection check (ADR-0013 SS2.6) - never persisted. Takes
    the same shape as a credential create, plus the model to test with,
    since Model Playground has no server-side default per provider."""

    provider: str
    api_key: str = Field(min_length=1, max_length=2000)
    base_url: str | None = Field(default=None, min_length=1, max_length=500)
    model: str = Field(min_length=1, max_length=100)

    @field_validator("provider")
    @classmethod
    def _validate_provider(cls, v: str) -> str:
        return _check_provider(v)

    @field_validator("base_url")
    @classmethod
    def _validate_base_url_scheme(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _check_base_url(v)

    @model_validator(mode="after")
    def _validate(self) -> "ProviderConnectionTestIn":
        spec = PROVIDER_REGISTRY[self.provider]
        if spec.requires_base_url and not self.base_url:
            raise ValueError(f"Provider '{self.provider}' requires a base_url")
        if not spec.requires_base_url and self.base_url:
            raise ValueError(f"Provider '{self.provider}' does not accept a base_url")
        _check_model(self.provider, self.model)
        return self


class ProviderConnectionTestOut(BaseModel):
    success: bool
    message: str
