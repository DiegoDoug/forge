from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class AdapterResult:
    response_text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class ProviderAdapter(Protocol):
    """One provider's outbound-call implementation. Adapters own their own
    client construction and never see any provider's key but their own -
    ``runs.py`` decrypts exactly the credential for the target being called
    and passes it in per-call (ADR-0011 SS2.3).

    ``base_url`` is optional and ignored by adapters that don't need it
    (OpenAI, Anthropic own a fixed client-construction path); it exists so
    ``runs.py`` can call every adapter uniformly without branching on
    provider (ADR-0013 SS2.5) - the OpenAI-compatible adapter uses it to
    target a fixed vendor endpoint or a user-supplied one."""

    async def complete(
        self, *, api_key: str, model: str, prompt: str, base_url: str | None = None
    ) -> AdapterResult: ...
