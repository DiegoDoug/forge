from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import NotFoundError
from app.models.activity import ActivityAction
from app.models.base import utcnow
from app.models.prompt_studio import Prompt, PromptVersion
from app.schemas.prompt_studio import PromptCreate, PromptUpdateContent, PromptUpdateMeta
from app.services import activity


def _dump_variables(variables: list) -> str:
    return json.dumps([v.model_dump() for v in variables])


def _dump_tags(tags: list[str]) -> str:
    return json.dumps(tags)


async def _get_prompt_or_404(session: AsyncSession, prompt_id: str) -> Prompt:
    result = await session.execute(select(Prompt).where(Prompt.id == prompt_id))
    prompt = result.scalar_one_or_none()
    if prompt is None:
        raise NotFoundError("Prompt not found")
    return prompt


async def create(session: AsyncSession, data: PromptCreate) -> Prompt:
    prompt = Prompt(
        name=data.name,
        description=data.description,
        body=data.body,
        variables_json=_dump_variables(data.variables),
        tags_json=_dump_tags(data.tags),
        version_number=1,
    )
    session.add(prompt)
    await session.flush()  # need prompt.id before the version row references it

    session.add(
        PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            body=prompt.body,
            variables_json=prompt.variables_json,
            note="Initial version",
        )
    )
    activity.record(session, ActivityAction.created, "prompt", prompt.id, f'Created "{prompt.name}"')
    await session.commit()
    await session.refresh(prompt)
    return prompt


async def get(session: AsyncSession, prompt_id: str) -> Prompt:
    return await _get_prompt_or_404(session, prompt_id)


async def list_prompts(session: AsyncSession, search: str | None = None, tag: str | None = None) -> list[Prompt]:
    query = select(Prompt).order_by(Prompt.updated_at.desc())
    if search:
        like = f"%{search}%"
        query = query.where((Prompt.name.ilike(like)) | (Prompt.description.ilike(like)))
    result = await session.execute(query)
    prompts = list(result.scalars().all())
    if tag:
        prompts = [p for p in prompts if tag in json.loads(p.tags_json)]
    return prompts


async def update_metadata(session: AsyncSession, prompt_id: str, data: PromptUpdateMeta) -> Prompt:
    """Metadata-only edit: name/description/tags. Never touches version_number
    or creates a PromptVersion row - only body/variables changes are versioned
    (update_content, below)."""
    prompt = await _get_prompt_or_404(session, prompt_id)

    if data.name is not None:
        prompt.name = data.name
    if data.description is not None:
        prompt.description = data.description
    if data.tags is not None:
        prompt.tags_json = _dump_tags(data.tags)
    prompt.updated_at = utcnow()

    session.add(prompt)
    activity.record(session, ActivityAction.updated, "prompt", prompt.id, f'Updated "{prompt.name}"')
    await session.commit()
    await session.refresh(prompt)
    return prompt


async def update_content(session: AsyncSession, prompt_id: str, data: PromptUpdateContent) -> Prompt:
    """Versioning operation. The content this prompt held *before* this call
    already has its own immutable PromptVersion row (written either by
    create(), or by whichever prior update_content()/restore_version() call
    last made it current) - so nothing needs to be re-snapshotted here. This
    call only needs to write ONE new row: the new content, at the next
    version number. That keeps exactly one row per version number, with no
    redundant duplicate entries."""
    prompt = await _get_prompt_or_404(session, prompt_id)

    new_version_number = prompt.version_number + 1
    session.add(
        PromptVersion(
            prompt_id=prompt.id,
            version_number=new_version_number,
            body=data.body,
            variables_json=_dump_variables(data.variables),
            note="Edited",
        )
    )

    prompt.body = data.body
    prompt.variables_json = _dump_variables(data.variables)
    prompt.version_number = new_version_number
    prompt.updated_at = utcnow()

    session.add(prompt)
    activity.record(
        session, ActivityAction.updated, "prompt", prompt.id, f'Saved v{prompt.version_number} of "{prompt.name}"'
    )
    await session.commit()
    await session.refresh(prompt)
    return prompt


async def delete(session: AsyncSession, prompt_id: str) -> None:
    prompt = await _get_prompt_or_404(session, prompt_id)
    name = prompt.name
    await session.delete(prompt)  # cascades to PromptVersion rows via the relationship's cascade kwarg
    activity.record(session, ActivityAction.deleted, "prompt", prompt_id, f'Deleted "{name}"')
    await session.commit()


async def duplicate(session: AsyncSession, prompt_id: str) -> Prompt:
    """Creates a brand-new, fully independent prompt (own id, own version
    history starting at 1) copying the source's *current* body/variables/tags.
    No source_prompt_id foreign key is stored - per 01_SPEC.md §3.10 the
    duplicate is intentionally a fresh entity, not linked to its source."""
    source = await _get_prompt_or_404(session, prompt_id)

    new_prompt = Prompt(
        name=f"{source.name} (copy)",
        description=source.description,
        body=source.body,
        variables_json=source.variables_json,
        tags_json=source.tags_json,
        version_number=1,
    )
    session.add(new_prompt)
    await session.flush()

    session.add(
        PromptVersion(
            prompt_id=new_prompt.id,
            version_number=1,
            body=new_prompt.body,
            variables_json=new_prompt.variables_json,
            note=f'Duplicated from "{source.name}"',
        )
    )
    activity.record(
        session, ActivityAction.created, "prompt", new_prompt.id, f'Duplicated "{source.name}" as "{new_prompt.name}"'
    )
    await session.commit()
    await session.refresh(new_prompt)
    return new_prompt


async def list_versions(session: AsyncSession, prompt_id: str) -> list[PromptVersion]:
    await _get_prompt_or_404(session, prompt_id)
    result = await session.execute(
        select(PromptVersion).where(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc())
    )
    return list(result.scalars().all())


async def get_version(session: AsyncSession, prompt_id: str, version_id: str) -> PromptVersion:
    """Guards against a version id from a *different* prompt being readable
    through this prompt's URL - the WHERE clause requires both to match, so a
    mismatch 404s exactly like a nonexistent id (01_SPEC.md / 06_API.md §3)."""
    result = await session.execute(
        select(PromptVersion).where(PromptVersion.id == version_id, PromptVersion.prompt_id == prompt_id)
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise NotFoundError("Prompt version not found")
    return version


async def restore_version(session: AsyncSession, prompt_id: str, version_id: str) -> Prompt:
    """The prompt's current content (before this call) is already safely
    recorded in its own PromptVersion row (see update_content's docstring) -
    restoring only needs to write ONE new row for the *restored* content, at
    the next version number, then apply it as current. Version numbers are
    never reused or decremented; restoring an old version always moves the
    counter forward."""
    prompt = await _get_prompt_or_404(session, prompt_id)
    target = await get_version(session, prompt_id, version_id)

    new_version_number = prompt.version_number + 1
    session.add(
        PromptVersion(
            prompt_id=prompt.id,
            version_number=new_version_number,
            body=target.body,
            variables_json=target.variables_json,
            note=f"Restored from v{target.version_number}",
        )
    )

    prompt.body = target.body
    prompt.variables_json = target.variables_json
    prompt.version_number = new_version_number
    prompt.updated_at = utcnow()

    session.add(prompt)
    activity.record(
        session,
        ActivityAction.updated,
        "prompt",
        prompt.id,
        f'Restored v{target.version_number} of "{prompt.name}"',
    )
    await session.commit()
    await session.refresh(prompt)
    return prompt
