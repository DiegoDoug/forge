from __future__ import annotations

from .base import AdapterResult

_DEFAULT_MAX_TOKENS = 4096


class AnthropicAdapter:
    async def complete(
        self, *, api_key: str, model: str, prompt: str, base_url: str | None = None
    ) -> AdapterResult:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=api_key)
        resp = await client.messages.create(
            model=model,
            max_tokens=_DEFAULT_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text").strip()
        usage = resp.usage
        return AdapterResult(
            response_text=text,
            prompt_tokens=usage.input_tokens if usage else None,
            completion_tokens=usage.output_tokens if usage else None,
        )
