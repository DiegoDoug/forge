from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.errors import AppError, NotFoundError
from app.models.activity import ActivityAction
from app.models.base import utcnow
from app.models.document import Document
from app.models.model_playground import PlaygroundRun
from app.models.note import Note
from app.models.project import Project
from app.models.secrets import Secret
from app.schemas.projects import ProjectCreateIn, ProjectUpdateIn
from app.services import activity
from app.services.model_playground import runs as model_playground_runs
from app.services.model_playground.runs import RunTarget

_CHILD_MODELS = (Secret, Note, Document, PlaygroundRun)


@dataclass
class ProjectCounts:
    secret_count: int
    note_count: int
    document_count: int


async def _get_or_404(session: AsyncSession, project_id: str) -> Project:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise NotFoundError("Project not found")
    return project


async def _counts_for(session: AsyncSession, project_id: str) -> ProjectCounts:
    secret_count = (
        await session.execute(select(func.count()).select_from(Secret).where(Secret.project_id == project_id))
    ).scalar_one()
    note_count = (
        await session.execute(select(func.count()).select_from(Note).where(Note.project_id == project_id))
    ).scalar_one()
    document_count = (
        await session.execute(select(func.count()).select_from(Document).where(Document.project_id == project_id))
    ).scalar_one()
    return ProjectCounts(secret_count=secret_count, note_count=note_count, document_count=document_count)


async def list_projects(session: AsyncSession, *, archived: bool = False) -> list[tuple[Project, ProjectCounts]]:
    result = await session.execute(
        select(Project).where(Project.archived == archived).order_by(Project.updated_at.desc())
    )
    projects = list(result.scalars().all())
    return [(p, await _counts_for(session, p.id)) for p in projects]


async def get_project(session: AsyncSession, project_id: str) -> tuple[Project, ProjectCounts]:
    project = await _get_or_404(session, project_id)
    return project, await _counts_for(session, project.id)


async def create_project(session: AsyncSession, data: ProjectCreateIn) -> tuple[Project, ProjectCounts]:
    project = Project(
        name=data.name,
        description=data.description,
        color=data.color,
        default_provider=data.default_provider,
        default_model=data.default_model,
    )
    session.add(project)
    await session.flush()
    activity.record(session, ActivityAction.created, "project", project.id, f'Created project "{project.name}"')
    await session.commit()
    return await get_project(session, project.id)


async def update_project(session: AsyncSession, project_id: str, data: ProjectUpdateIn) -> tuple[Project, ProjectCounts]:
    project = await _get_or_404(session, project_id)

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.color is not None:
        project.color = data.color
    if data.archived is not None:
        project.archived = data.archived
    if data.clear_default_ai:
        project.default_provider = None
        project.default_model = None
    elif data.default_provider is not None or data.default_model is not None:
        project.default_provider = data.default_provider
        project.default_model = data.default_model

    project.updated_at = utcnow()
    session.add(project)
    activity.record(session, ActivityAction.updated, "project", project.id, f'Updated project "{project.name}"')
    await session.commit()
    return await get_project(session, project.id)


async def delete_project(session: AsyncSession, project_id: str) -> None:
    """Unscopes every Secret/Note/Document/PlaygroundRun that referenced this
    project, then deletes the Project row. Never deletes the children
    themselves — an organizational label is not an owner (ADR-0014 SS2)."""
    project = await _get_or_404(session, project_id)
    name = project.name

    for model in _CHILD_MODELS:
        result = await session.execute(select(model).where(model.project_id == project_id))
        for row in result.scalars().all():
            row.project_id = None
            session.add(row)

    await session.delete(project)
    activity.record(session, ActivityAction.deleted, "project", project_id, f'Deleted project "{name}"')
    await session.commit()


async def run_project_prompt(session: AsyncSession, project_id: str, prompt: str) -> PlaygroundRun:
    project = await _get_or_404(session, project_id)
    if not project.default_provider or not project.default_model:
        raise AppError(
            "Project has no default AI provider/model configured",
            status_code=400,
            code="project_ai_not_configured",
        )

    run = await model_playground_runs.create_run(
        session,
        prompt=prompt,
        targets=[RunTarget(provider=project.default_provider, model=project.default_model)],
    )
    run.project_id = project_id
    session.add(run)
    await session.commit()
    # refresh() would expire `results` and force a lazy-load outside of an
    # async context on the next access - re-fetch with the eager-loaded
    # query create_run/get_run already use instead.
    return await model_playground_runs.get_run(session, run.id)


async def list_project_runs(session: AsyncSession, project_id: str, *, limit: int = 20) -> list[PlaygroundRun]:
    await _get_or_404(session, project_id)
    result = await session.execute(
        select(PlaygroundRun)
        .options(selectinload(PlaygroundRun.results))
        .where(PlaygroundRun.project_id == project_id)
        .order_by(PlaygroundRun.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().unique().all())
