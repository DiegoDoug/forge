from __future__ import annotations

from .base import AdapterResult


class OpenAIAdapter:
    async def complete(self, *, api_key: str, model: str, prompt: str) -> AdapterResult:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
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
