from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.errors import AppError, NotFoundError
from app.models.activity import ActivityAction
from app.models.model_playground import PlaygroundResult, PlaygroundRun, ProviderCredential
from app.services import activity
from app.services.model_playground.credentials import decrypt_api_key
from app.services.model_playground.errors import to_user_message
from app.services.model_playground.providers import PROVIDER_REGISTRY

logger = logging.getLogger("forge.model_playground")

TIMEOUT_SECONDS = 60.0  # per ADR-0011 SS2.5


@dataclass
class RunTarget:
    provider: str
    model: str


def _run_query():
    return select(PlaygroundRun).options(selectinload(PlaygroundRun.results))


async def _get_run_or_404(session: AsyncSession, run_id: str) -> PlaygroundRun:
    result = await session.execute(_run_query().where(PlaygroundRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise NotFoundError("Run not found")
    return run


async def _call_target(*, api_key: str, base_url: str | None, prompt: str, target: RunTarget) -> PlaygroundResult:
    spec = PROVIDER_REGISTRY[target.provider]
    started = time.monotonic()
    try:
        outcome = await asyncio.wait_for(
            spec.adapter.complete(api_key=api_key, model=target.model, prompt=prompt, base_url=base_url),
            timeout=TIMEOUT_SECONDS,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        return PlaygroundResult(
            run_id="",  # set by caller after the PlaygroundRun exists
            provider=target.provider,
            model=target.model,
            status="success",
            response_text=outcome.response_text,
            latency_ms=latency_ms,
            prompt_tokens=outcome.prompt_tokens,
            completion_tokens=outcome.completion_tokens,
        )
    except asyncio.TimeoutError:
        return PlaygroundResult(
            run_id="",
            provider=target.provider,
            model=target.model,
            status="timeout",
            error_message=f"Timed out after {int(TIMEOUT_SECONDS)}s.",
            latency_ms=int((time.monotonic() - started) * 1000),
        )
    except Exception as exc:  # noqa: BLE001 - deliberately broad, isolates one target's failure from the rest
        logger.exception("Model Playground call failed for provider=%s model=%s", target.provider, target.model)
        return PlaygroundResult(
            run_id="",
            provider=target.provider,
            model=target.model,
            status="error",
            error_message=to_user_message(exc),
            latency_ms=int((time.monotonic() - started) * 1000),
        )


async def create_run(session: AsyncSession, *, prompt: str, targets: list[RunTarget]) -> PlaygroundRun:
    distinct_providers = {t.provider for t in targets}
    result = await session.execute(
        select(ProviderCredential).where(ProviderCredential.provider.in_(distinct_providers))
    )
    found = {c.provider: c for c in result.scalars().all()}
    missing = distinct_providers - found.keys()
    if missing:
        raise AppError(
            f"No credential configured for provider(s): {', '.join(sorted(missing))}",
            status_code=400,
            code="provider_not_configured",
        )

    api_keys: dict[str, str] = {}
    base_urls: dict[str, str | None] = {}
    for provider, credential in found.items():
        api_keys[provider] = await decrypt_api_key(credential)
        base_urls[provider] = credential.base_url

    results = await asyncio.gather(
        *(
            _call_target(api_key=api_keys[t.provider], base_url=base_urls[t.provider], prompt=prompt, target=t)
            for t in targets
        )
    )

    run = PlaygroundRun(prompt=prompt)
    session.add(run)
    await session.flush()
    for r in results:
        r.run_id = run.id
        session.add(r)

    activity.record(session, ActivityAction.created, "playground_run", run.id, "Ran a Model Playground comparison")
    await session.commit()
    return await _get_run_or_404(session, run.id)


async def list_runs(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[PlaygroundRun]:
    result = await session.execute(
        _run_query().order_by(PlaygroundRun.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().unique().all())


async def get_run(session: AsyncSession, run_id: str) -> PlaygroundRun:
    return await _get_run_or_404(session, run_id)


async def delete_run(session: AsyncSession, run_id: str) -> None:
    run = await _get_run_or_404(session, run_id)
    await session.delete(run)
    activity.record(session, ActivityAction.deleted, "playground_run", run_id, "Deleted a Model Playground run")
    await session.commit()
