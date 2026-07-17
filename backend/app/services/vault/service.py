from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import or_, select

from app.core.errors import NotFoundError
from app.core.security import get_vault_crypto
from app.models.activity import ActivityAction
from app.models.base import utcnow
from app.models.vault import Folder, Secret, SecretVersion, Tag
from app.services import activity
from app.schemas.vault import (
    FolderIn,
    SecretCreateIn,
    SecretMetadata,
    SecretUpdateIn,
    TagIn,
)


def _secret_query():
    return select(Secret).options(selectinload(Secret.tags), selectinload(Secret.folder))


async def _get_secret_or_404(session: AsyncSession, secret_id: str) -> Secret:
    result = await session.execute(_secret_query().where(Secret.id == secret_id))
    secret = result.scalar_one_or_none()
    if secret is None:
        raise NotFoundError("Secret not found")
    return secret


async def _resolve_tags(session: AsyncSession, tag_ids: list[str]) -> list[Tag]:
    if not tag_ids:
        return []
    result = await session.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    return list(result.scalars().all())


def _encrypt_metadata(metadata: SecretMetadata) -> bytes:
    crypto = get_vault_crypto()
    return crypto.encrypt_str(metadata.model_dump_json())


def _decrypt_metadata(blob: bytes | None) -> SecretMetadata:
    if not blob:
        return SecretMetadata()
    crypto = get_vault_crypto()
    return SecretMetadata.model_validate_json(crypto.decrypt_str(blob))


async def list_secrets(
    session: AsyncSession, *, folder_id: str | None = None, tag_id: str | None = None, query: str | None = None
) -> list[Secret]:
    stmt = _secret_query()
    if folder_id:
        stmt = stmt.where(Secret.folder_id == folder_id)
    if query:
        like = f"%{query}%"
        stmt = stmt.where(or_(Secret.name.ilike(like)))
    stmt = stmt.order_by(Secret.favorite.desc(), Secret.name)
    result = await session.execute(stmt)
    secrets = list(result.scalars().unique().all())
    if tag_id:
        secrets = [s for s in secrets if any(t.id == tag_id for t in s.tags)]
    return secrets


async def get_secret(session: AsyncSession, secret_id: str, *, reveal: bool = False) -> tuple[Secret, str | None, SecretMetadata]:
    secret = await _get_secret_or_404(session, secret_id)
    metadata = _decrypt_metadata(secret.encrypted_metadata)
    value = None
    if reveal:
        crypto = get_vault_crypto()
        value = crypto.decrypt_str(secret.encrypted_value)
        activity.record(session, ActivityAction.viewed, "secret", secret.id, f'Revealed "{secret.name}"')
        await session.commit()
    return secret, value, metadata


async def create_secret(session: AsyncSession, data: SecretCreateIn) -> Secret:
    crypto = get_vault_crypto()
    secret = Secret(
        name=data.name,
        type=data.type,
        folder_id=data.folder_id,
        encrypted_value=crypto.encrypt_str(data.value),
        encrypted_metadata=_encrypt_metadata(data.metadata),
        favorite=data.favorite,
    )
    secret.tags = await _resolve_tags(session, data.tag_ids)
    session.add(secret)
    await session.flush()
    session.add(SecretVersion(secret_id=secret.id, encrypted_value=secret.encrypted_value))
    activity.record(session, ActivityAction.created, "secret", secret.id, f'Created "{secret.name}"')
    await session.commit()
    return await _get_secret_or_404(session, secret.id)


async def update_secret(session: AsyncSession, secret_id: str, data: SecretUpdateIn) -> Secret:
    secret = await _get_secret_or_404(session, secret_id)
    crypto = get_vault_crypto()

    if data.name is not None:
        secret.name = data.name
    if data.type is not None:
        secret.type = data.type
    if "folder_id" in data.model_fields_set:
        secret.folder_id = data.folder_id
    if data.favorite is not None:
        secret.favorite = data.favorite
    if data.tag_ids is not None:
        secret.tags = await _resolve_tags(session, data.tag_ids)
    if data.metadata is not None:
        secret.encrypted_metadata = _encrypt_metadata(data.metadata)
    if data.value is not None:
        session.add(SecretVersion(secret_id=secret.id, encrypted_value=secret.encrypted_value))
        secret.encrypted_value = crypto.encrypt_str(data.value)

    secret.updated_at = utcnow()
    session.add(secret)
    activity.record(session, ActivityAction.updated, "secret", secret.id, f'Updated "{secret.name}"')
    await session.commit()
    return await _get_secret_or_404(session, secret.id)


async def delete_secret(session: AsyncSession, secret_id: str) -> None:
    secret = await _get_secret_or_404(session, secret_id)
    name = secret.name
    await session.delete(secret)
    activity.record(session, ActivityAction.deleted, "secret", secret_id, f'Deleted "{name}"')
    await session.commit()


async def list_versions(session: AsyncSession, secret_id: str) -> list[SecretVersion]:
    await _get_secret_or_404(session, secret_id)
    result = await session.execute(
        select(SecretVersion).where(SecretVersion.secret_id == secret_id).order_by(SecretVersion.created_at.desc())
    )
    return list(result.scalars().all())


async def reveal_version(session: AsyncSession, secret_id: str, version_id: str) -> SecretVersion:
    result = await session.execute(
        select(SecretVersion).where(SecretVersion.id == version_id, SecretVersion.secret_id == secret_id)
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise NotFoundError("Secret version not found")
    return version


def decrypt_version_value(version: SecretVersion) -> str:
    return get_vault_crypto().decrypt_str(version.encrypted_value)


# --- Folders --------------------------------------------------------------


async def list_folders(session: AsyncSession) -> list[Folder]:
    result = await session.execute(select(Folder).order_by(Folder.name))
    return list(result.scalars().all())


async def create_folder(session: AsyncSession, data: FolderIn) -> Folder:
    folder = Folder(name=data.name, parent_id=data.parent_id)
    session.add(folder)
    await session.commit()
    await session.refresh(folder)
    return folder


async def delete_folder(session: AsyncSession, folder_id: str) -> None:
    result = await session.execute(select(Folder).where(Folder.id == folder_id))
    folder = result.scalar_one_or_none()
    if folder is None:
        raise NotFoundError("Folder not found")
    await session.delete(folder)
    await session.commit()


# --- Tags -------------------------------------------------------------


async def list_tags(session: AsyncSession) -> list[Tag]:
    result = await session.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars().all())


async def create_tag(session: AsyncSession, data: TagIn) -> Tag:
    tag = Tag(name=data.name, color=data.color)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


async def delete_tag(session: AsyncSession, tag_id: str) -> None:
    result = await session.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise NotFoundError("Tag not found")
    await session.delete(tag)
    await session.commit()
