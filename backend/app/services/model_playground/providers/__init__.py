from __future__ import annotations

from dataclasses import dataclass

from .anthropic_adapter import AnthropicAdapter
from .base import AdapterResult, ProviderAdapter
from .openai_adapter import OpenAIAdapter
from .openai_compatible_adapter import OpenAICompatibleAdapter


@dataclass(frozen=True)
class ProviderSpec:
    key: str
    display_name: str
    models: tuple[str, ...]
    adapter: ProviderAdapter
    # True only for the user-configurable Custom provider (ADR-0013 SS2.3) -
    # its ProviderCredential.base_url is required and passed through to the
    # adapter per-call; every fixed-endpoint provider rejects a base_url.
    requires_base_url: bool = False
    # True only where Forge can't know the model catalogue ahead of time
    # (Custom provider) - RunTargetIn accepts any non-empty model string
    # instead of validating membership in `models` (which is empty here).
    allows_custom_model: bool = False


# Provider list per ADR-0012 (v1: OpenAI, Anthropic) extended by ADR-0013
# (DeepSeek, Kimi, GLM, Gemini, Custom) - nothing more without a new ADR.
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
    "deepseek": ProviderSpec(
        key="deepseek",
        display_name="DeepSeek",
        models=("deepseek-chat", "deepseek-reasoner"),
        adapter=OpenAICompatibleAdapter(default_base_url="https://api.deepseek.com/v1"),
    ),
    "kimi": ProviderSpec(
        key="kimi",
        display_name="Kimi (Moonshot)",
        models=("moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"),
        adapter=OpenAICompatibleAdapter(default_base_url="https://api.moonshot.cn/v1"),
    ),
    "glm": ProviderSpec(
        key="glm",
        display_name="GLM (Zhipu)",
        models=("glm-4", "glm-4-air", "glm-4-flash"),
        adapter=OpenAICompatibleAdapter(default_base_url="https://open.bigmodel.cn/api/paas/v4"),
    ),
    "gemini": ProviderSpec(
        key="gemini",
        display_name="Gemini",
        models=("gemini-2.5-pro", "gemini-2.5-flash"),
        adapter=OpenAICompatibleAdapter(
            default_base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ),
    ),
    "custom": ProviderSpec(
        key="custom",
        display_name="Custom (OpenAI-compatible)",
        models=(),
        adapter=OpenAICompatibleAdapter(),
        requires_base_url=True,
        allows_custom_model=True,
    ),
}

__all__ = ["AdapterResult", "ProviderAdapter", "ProviderSpec", "PROVIDER_REGISTRY"]
