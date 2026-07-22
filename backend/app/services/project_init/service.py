from __future__ import annotations

import json

import pydantic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import AppError, NotFoundError
from app.models.activity import ActivityAction
from app.models.project_init import ProjectInitGeneration
from app.schemas.project_init import AiInstructionsConfig, FdkPhaseConfig
from app.services import activity

from . import renderer
from .zipper import to_zip

HISTORY_LIMIT_DEFAULT = 20


def _validate_config(kind: str, raw_config: dict) -> FdkPhaseConfig | AiInstructionsConfig:
    try:
        if kind == "fdk_phase":
            return FdkPhaseConfig.model_validate(raw_config)
        if kind == "ai_instructions":
            return AiInstructionsConfig.model_validate(raw_config)
    except pydantic.ValidationError as exc:
        raise AppError(str(exc), status_code=422, code="validation_error") from exc
    raise AppError(f"Unknown template kind: {kind}", status_code=422, code="validation_error")


def _display_name(config: FdkPhaseConfig | AiInstructionsConfig) -> str:
    if isinstance(config, FdkPhaseConfig):
        return config.phase_name
    return config.project_name


def _zip_filename(config: FdkPhaseConfig | AiInstructionsConfig) -> str:
    if isinstance(config, FdkPhaseConfig):
        return f"{renderer.phase_folder_name(config.phase_number, config.phase_name)}.zip"
    return f"{renderer.project_slug(config.project_name)}-ai-instructions.zip"


async def _get_or_404(session: AsyncSession, generation_id: str) -> ProjectInitGeneration:
    result = await session.execute(select(ProjectInitGeneration).where(ProjectInitGeneration.id == generation_id))
    generation = result.scalar_one_or_none()
    if generation is None:
        raise NotFoundError("Generation not found")
    return generation


async def generate(session: AsyncSession, kind: str, raw_config: dict) -> tuple[ProjectInitGeneration, dict[str, str]]:
    config = _validate_config(kind, raw_config)
    files = renderer.render(kind, config)
    name = _display_name(config)

    record = ProjectInitGeneration(kind=kind, name=name, config=json.dumps(raw_config))
    session.add(record)
    activity.record(session, ActivityAction.created, "project_init_generation", record.id, f'Generated "{name}"')
    await session.commit()
    await session.refresh(record)
    return record, files


async def render_zip_for(session: AsyncSession, generation_id: str) -> tuple[ProjectInitGeneration, bytes, str]:
    record = await _get_or_404(session, generation_id)
    raw_config = json.loads(record.config)
    config = _validate_config(record.kind, raw_config)
    files = renderer.render(record.kind, config)
    zip_bytes = to_zip(files)
    filename = _zip_filename(config)
    return record, zip_bytes, filename


async def list_history(session: AsyncSession, limit: int = HISTORY_LIMIT_DEFAULT) -> list[ProjectInitGeneration]:
    result = await session.execute(
        select(ProjectInitGeneration).order_by(ProjectInitGeneration.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def delete(session: AsyncSession, generation_id: str) -> None:
    record = await _get_or_404(session, generation_id)
    await session.delete(record)
    await session.commit()
