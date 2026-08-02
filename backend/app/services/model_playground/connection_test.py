from __future__ import annotations

import asyncio
import logging

from app.services.model_playground.errors import to_user_message
from app.services.model_playground.providers import PROVIDER_REGISTRY

logger = logging.getLogger("forge.model_playground")

# Shorter than a real run's TIMEOUT_SECONDS (runs.py) - this is a synchronous
# "wait for the result" UI action (ADR-0013 SS2.6), not a background run.
TEST_TIMEOUT_SECONDS = 20.0
_TEST_PROMPT = "Respond with only the single word: ok"


async def test_connection(*, provider: str, api_key: str, base_url: str | None, model: str) -> tuple[bool, str]:
    """Exercise the real adapter path with request-supplied, never-persisted
    credentials. Never logs the api_key or base_url - only the provider key
    and, on failure, the exception's class name (docs/Security.md "Input
    handling": errors never leak internals)."""
    spec = PROVIDER_REGISTRY[provider]
    try:
        await asyncio.wait_for(
            spec.adapter.complete(api_key=api_key, model=model, prompt=_TEST_PROMPT, base_url=base_url),
            timeout=TEST_TIMEOUT_SECONDS,
        )
        return True, "Connection succeeded."
    except asyncio.TimeoutError:
        return False, f"Timed out after {int(TEST_TIMEOUT_SECONDS)}s."
    except Exception as exc:  # noqa: BLE001 - deliberately broad, translated to a safe message below
        logger.info("Model Playground connection test failed for provider=%s: %s", provider, type(exc).__name__)
        return False, to_user_message(exc)
