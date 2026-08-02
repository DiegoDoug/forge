from __future__ import annotations

from .base import AdapterResult


class OpenAICompatibleAdapter:
    """Serves any provider whose chat API is OpenAI-compatible (DeepSeek,
    Kimi/Moonshot, GLM/Zhipu, Gemini via Google's OpenAI-compat layer, and
    the user-configurable Custom provider) via the ``openai`` SDK pointed at
    a different ``base_url`` - the same generic pattern
    ``services/ingest/vision.py`` already uses (see ADR-0013 SS2.1).

    ``default_base_url`` is set for fixed-endpoint named providers (DeepSeek,
    Kimi, GLM, Gemini); left ``None`` for the Custom provider, whose base URL
    is supplied per-call from the user's stored credential instead."""

    def __init__(self, *, default_base_url: str | None = None) -> None:
        self._default_base_url = default_base_url

    @property
    def default_base_url(self) -> str | None:
        return self._default_base_url

    async def complete(
        self, *, api_key: str, model: str, prompt: str, base_url: str | None = None
    ) -> AdapterResult:
        from openai import AsyncOpenAI

        resolved_base_url = base_url or self._default_base_url
        client = AsyncOpenAI(api_key=api_key, base_url=resolved_base_url)
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        text = (resp.choices[0].message.content or "").strip()
        usage = resp.usage
        return AdapterResult(
            response_text=text,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
        )
