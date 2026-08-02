from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.models.model_playground import PlaygroundResult, PlaygroundRun, ProviderCredential
from app.schemas.model_playground import (
    PROMPT_EXCERPT_LENGTH,
    PlaygroundRunIn,
    PlaygroundRunListOut,
    PlaygroundRunOut,
    ProviderAvailability,
    ProviderConnectionTestIn,
    ProviderConnectionTestOut,
    ProviderCredentialIn,
    ProviderCredentialListOut,
    ProviderCredentialOut,
)
from app.services.model_playground import connection_test as connection_test_service
from app.services.model_playground import credentials as credentials_service
from app.services.model_playground import runs as runs_service
from app.services.model_playground.runs import RunTarget

router = APIRouter(prefix="/model-playground", tags=["model-playground"], dependencies=[AuthDep])


def _to_credential_out(credential: ProviderCredential) -> ProviderCredentialOut:
    return ProviderCredentialOut(
        id=credential.id,
        provider=credential.provider,
        label=credential.label,
        base_url=credential.base_url,
        created_at=credential.created_at,
        updated_at=credential.updated_at,
    )


def _to_result_out(result: PlaygroundResult) -> dict:
    return {
        "id": result.id,
        "provider": result.provider,
        "model": result.model,
        "status": result.status,
        "response_text": result.response_text,
        "error_message": result.error_message,
        "latency_ms": result.latency_ms,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
    }


def _to_run_out(run: PlaygroundRun) -> PlaygroundRunOut:
    return PlaygroundRunOut(
        id=run.id,
        prompt=run.prompt,
        created_at=run.created_at,
        results=[_to_result_out(r) for r in run.results],
    )


def _excerpt(prompt: str) -> str:
    if len(prompt) <= PROMPT_EXCERPT_LENGTH:
        return prompt
    return prompt[:PROMPT_EXCERPT_LENGTH].rstrip() + "…"


def _to_run_list_out(runs: list[PlaygroundRun]) -> PlaygroundRunListOut:
    return PlaygroundRunListOut(
        items=[
            {
                "id": run.id,
                "prompt_excerpt": _excerpt(run.prompt),
                "providers": sorted({r.provider for r in run.results}),
                "created_at": run.created_at,
            }
            for run in runs
        ]
    )


@router.get("/providers", response_model=list[ProviderAvailability])
async def list_providers(session: SessionDep) -> list[ProviderAvailability]:
    availability = await credentials_service.list_provider_availability(session)
    return [ProviderAvailability(**a) for a in availability]


@router.post("/providers/test-connection", response_model=ProviderConnectionTestOut)
async def test_provider_connection(body: ProviderConnectionTestIn) -> ProviderConnectionTestOut:
    success, message = await connection_test_service.test_connection(
        provider=body.provider, api_key=body.api_key, base_url=body.base_url, model=body.model
    )
    return ProviderConnectionTestOut(success=success, message=message)


@router.get("/credentials", response_model=ProviderCredentialListOut)
async def list_credentials(session: SessionDep) -> ProviderCredentialListOut:
    creds = await credentials_service.list_credentials(session)
    return ProviderCredentialListOut(items=[_to_credential_out(c) for c in creds])


@router.post("/credentials", response_model=ProviderCredentialOut, status_code=201)
async def create_credential(body: ProviderCredentialIn, session: SessionDep) -> ProviderCredentialOut:
    credential = await credentials_service.create_or_replace_credential(
        session, provider=body.provider, label=body.label, api_key=body.api_key, base_url=body.base_url
    )
    return _to_credential_out(credential)


@router.delete("/credentials/{credential_id}", status_code=204)
async def delete_credential(credential_id: str, session: SessionDep) -> None:
    await credentials_service.delete_credential(session, credential_id)


@router.post("/runs", response_model=PlaygroundRunOut, status_code=201)
async def create_run(body: PlaygroundRunIn, session: SessionDep) -> PlaygroundRunOut:
    targets = [RunTarget(provider=t.provider, model=t.model) for t in body.targets]
    run = await runs_service.create_run(session, prompt=body.prompt, targets=targets)
    return _to_run_out(run)


@router.get("/runs", response_model=PlaygroundRunListOut)
async def list_runs(session: SessionDep, limit: int = 50, offset: int = 0) -> PlaygroundRunListOut:
    runs = await runs_service.list_runs(session, limit=limit, offset=offset)
    return _to_run_list_out(runs)


@router.get("/runs/{run_id}", response_model=PlaygroundRunOut)
async def get_run(run_id: str, session: SessionDep) -> PlaygroundRunOut:
    run = await runs_service.get_run(session, run_id)
    return _to_run_out(run)


@router.delete("/runs/{run_id}", status_code=204)
async def delete_run(run_id: str, session: SessionDep) -> None:
    await runs_service.delete_run(session, run_id)
