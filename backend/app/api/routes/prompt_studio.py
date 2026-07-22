from __future__ import annotations

import json

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.models.prompt_studio import Prompt, PromptVersion
from app.schemas.prompt_studio import (
    PromptCreate,
    PromptListOut,
    PromptOut,
    PromptUpdateContent,
    PromptUpdateMeta,
    PromptVersionListOut,
    PromptVersionOut,
)
from app.services.prompt_studio import service

router = APIRouter(prefix="/prompts", tags=["prompt-studio"], dependencies=[AuthDep])


def _to_prompt_out(prompt: Prompt) -> PromptOut:
    return PromptOut(
        id=prompt.id,
        name=prompt.name,
        description=prompt.description,
        body=prompt.body,
        variables=json.loads(prompt.variables_json),
        tags=json.loads(prompt.tags_json),
        version_number=prompt.version_number,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at,
    )


def _to_prompt_list_out(prompts: list[Prompt]) -> PromptListOut:
    return PromptListOut(
        items=[
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "tags": json.loads(p.tags_json),
                "version_number": p.version_number,
                "updated_at": p.updated_at,
            }
            for p in prompts
        ]
    )


def _to_version_out(version: PromptVersion) -> PromptVersionOut:
    return PromptVersionOut(
        id=version.id,
        version_number=version.version_number,
        body=version.body,
        variables=json.loads(version.variables_json),
        note=version.note,
        created_at=version.created_at,
    )


def _to_version_list_out(versions: list[PromptVersion]) -> PromptVersionListOut:
    return PromptVersionListOut(
        items=[
            {"id": v.id, "version_number": v.version_number, "note": v.note, "created_at": v.created_at}
            for v in versions
        ]
    )


@router.get("", response_model=PromptListOut)
async def list_prompts(session: SessionDep, search: str | None = None, tag: str | None = None) -> PromptListOut:
    prompts = await service.list_prompts(session, search=search, tag=tag)
    return _to_prompt_list_out(prompts)


@router.post("", response_model=PromptOut, status_code=201)
async def create_prompt(body: PromptCreate, session: SessionDep) -> PromptOut:
    prompt = await service.create(session, body)
    return _to_prompt_out(prompt)


@router.get("/{prompt_id}", response_model=PromptOut)
async def get_prompt(prompt_id: str, session: SessionDep) -> PromptOut:
    prompt = await service.get(session, prompt_id)
    return _to_prompt_out(prompt)


@router.patch("/{prompt_id}", response_model=PromptOut)
async def update_prompt_metadata(prompt_id: str, body: PromptUpdateMeta, session: SessionDep) -> PromptOut:
    prompt = await service.update_metadata(session, prompt_id, body)
    return _to_prompt_out(prompt)


@router.put("/{prompt_id}/content", response_model=PromptOut)
async def update_prompt_content(prompt_id: str, body: PromptUpdateContent, session: SessionDep) -> PromptOut:
    prompt = await service.update_content(session, prompt_id, body)
    return _to_prompt_out(prompt)


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: str, session: SessionDep) -> None:
    await service.delete(session, prompt_id)


@router.post("/{prompt_id}/duplicate", response_model=PromptOut, status_code=201)
async def duplicate_prompt(prompt_id: str, session: SessionDep) -> PromptOut:
    prompt = await service.duplicate(session, prompt_id)
    return _to_prompt_out(prompt)


@router.get("/{prompt_id}/versions", response_model=PromptVersionListOut)
async def list_prompt_versions(prompt_id: str, session: SessionDep) -> PromptVersionListOut:
    versions = await service.list_versions(session, prompt_id)
    return _to_version_list_out(versions)


@router.get("/{prompt_id}/versions/{version_id}", response_model=PromptVersionOut)
async def get_prompt_version(prompt_id: str, version_id: str, session: SessionDep) -> PromptVersionOut:
    version = await service.get_version(session, prompt_id, version_id)
    return _to_version_out(version)


@router.post("/{prompt_id}/versions/{version_id}/restore", response_model=PromptOut)
async def restore_prompt_version(prompt_id: str, version_id: str, session: SessionDep) -> PromptOut:
    prompt = await service.restore_version(session, prompt_id, version_id)
    return _to_prompt_out(prompt)
