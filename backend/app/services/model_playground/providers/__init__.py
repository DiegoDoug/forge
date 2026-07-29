from __future__ import annotations

from dataclasses import dataclass

from .anthropic_adapter import AnthropicAdapter
from .base import AdapterResult, ProviderAdapter
from .openai_adapter import OpenAIAdapter


@dataclass(frozen=True)
class ProviderSpec:
    key: str
    display_name: str
    models: tuple[str, ...]
    adapter: ProviderAdapter


# v1 provider list per ADR-0011 - exactly these two, nothing more without a
# new ADR (see IMPLEMENT.md "Autonomy Rules").
PROVIDER_REGISTRY: dict[str, ProviderSpec] = {
    "openai": ProviderSpec(
        key="openai",
        display_name="OpenAI",
        models=("gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"),
        adapter=OpenAIAdapter(),
    ),
    "anthropic": ProviderSpec(
        key="anthropic",
        display_name="Anthropic",
        models=("claude-opus-5", "claude-sonnet-5", "claude-fable-5", "claude-haiku-4-5-20251001"),
        adapter=AnthropicAdapter(),
    ),
}

__all__ = ["AdapterResult", "ProviderAdapter", "ProviderSpec", "PROVIDER_REGISTRY"]
