from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.models.model_playground import PlaygroundResult, PlaygroundRun
from app.models.project import Project
from app.schemas.model_playground import PROMPT_EXCERPT_LENGTH, PlaygroundRunListOut, PlaygroundRunOut
from app.schemas.projects import (
    ProjectAiRunIn,
    ProjectCreateIn,
    ProjectOut,
    ProjectSummaryOut,
    ProjectUpdateIn,
)
from app.services.projects import service
from app.services.projects.service import ProjectCounts

router = APIRouter(prefix="/projects", tags=["projects"], dependencies=[AuthDep])


def _to_out(project: Project, counts: ProjectCounts) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        color=project.color,
        archived=project.archived,
        default_provider=project.default_provider,
        default_model=project.default_model,
        secret_count=counts.secret_count,
        note_count=counts.note_count,
        document_count=counts.document_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _to_summary(project: Project, counts: ProjectCounts) -> ProjectSummaryOut:
    return ProjectSummaryOut(
        id=project.id,
        name=project.name,
        color=project.color,
        archived=project.archived,
        secret_count=counts.secret_count,
        note_count=counts.note_count,
        document_count=counts.document_count,
        updated_at=project.updated_at,
    )


def _excerpt(prompt: str) -> str:
    if len(prompt) <= PROMPT_EXCERPT_LENGTH:
        return prompt
    return prompt[:PROMPT_EXCERPT_LENGTH].rstrip() + "…"


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


@router.get("", response_model=list[ProjectSummaryOut])
async def list_projects(session: SessionDep, archived: bool = False) -> list[ProjectSummaryOut]:
    projects = await service.list_projects(session, archived=archived)
    return [_to_summary(p, c) for p, c in projects]


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(body: ProjectCreateIn, session: SessionDep) -> ProjectOut:
    project, counts = await service.create_project(session, body)
    return _to_out(project, counts)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, session: SessionDep) -> ProjectOut:
    project, counts = await service.get_project(session, project_id)
    return _to_out(project, counts)


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: str, body: ProjectUpdateIn, session: SessionDep) -> ProjectOut:
    project, counts = await service.update_project(session, project_id, body)
    return _to_out(project, counts)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, session: SessionDep) -> None:
    await service.delete_project(session, project_id)


@router.post("/{project_id}/ai/run", response_model=PlaygroundRunOut, status_code=201)
async def run_project_ai(project_id: str, body: ProjectAiRunIn, session: SessionDep) -> PlaygroundRunOut:
    run = await service.run_project_prompt(session, project_id, body.prompt)
    return _to_run_out(run)


@router.get("/{project_id}/ai/runs", response_model=PlaygroundRunListOut)
async def list_project_ai_runs(project_id: str, session: SessionDep, limit: int = 20) -> PlaygroundRunListOut:
    runs = await service.list_project_runs(session, project_id, limit=limit)
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
