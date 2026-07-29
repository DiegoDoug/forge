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
    and passes it in per-call (ADR-0011 SS2.3)."""

    async def complete(self, *, api_key: str, model: str, prompt: str) -> AdapterResult: ...
