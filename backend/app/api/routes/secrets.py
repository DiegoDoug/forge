from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import AuthDep, SessionDep
from app.schemas.secrets import (
    FolderIn,
    FolderOut,
    SecretCreateIn,
    SecretDetailOut,
    SecretSummaryOut,
    SecretUpdateIn,
    SecretVersionOut,
    SecretVersionValueOut,
    TagIn,
    TagOut,
)
from app.services.secrets import service

# No prefix baked in here — app/api/router.py mounts this router twice, once
# at /secrets and once at /vault (a compatibility alias for the pre-rename
# path, see ADR-0006: forge-docs/decisions/0006-vault-renamed-to-secrets.md).
router = APIRouter(tags=["secrets"], dependencies=[AuthDep])


def _summary(secret) -> SecretSummaryOut:
    return SecretSummaryOut(
        id=secret.id,
        name=secret.name,
        type=secret.type,
        folder_id=secret.folder_id,
        tags=[TagOut(id=t.id, name=t.name, color=t.color) for t in secret.tags],
        favorite=secret.favorite,
        created_at=secret.created_at,
        updated_at=secret.updated_at,
    )


@router.get("/secrets", response_model=list[SecretSummaryOut])
async def list_secrets(
    session: SessionDep,
    folder_id: str | None = None,
    tag_id: str | None = None,
    q: str | None = Query(default=None),
) -> list[SecretSummaryOut]:
    secrets = await service.list_secrets(session, folder_id=folder_id, tag_id=tag_id, query=q)
    return [_summary(s) for s in secrets]


@router.post("/secrets", response_model=SecretDetailOut, status_code=201)
async def create_secret(body: SecretCreateIn, session: SessionDep) -> SecretDetailOut:
    secret = await service.create_secret(session, body)
    return SecretDetailOut(**_summary(secret).model_dump(), value=None, metadata=body.metadata)


@router.get("/secrets/{secret_id}", response_model=SecretDetailOut)
async def get_secret(secret_id: str, session: SessionDep, reveal: bool = False) -> SecretDetailOut:
    secret, value, metadata = await service.get_secret(session, secret_id, reveal=reveal)
    return SecretDetailOut(**_summary(secret).model_dump(), value=value, metadata=metadata)


@router.patch("/secrets/{secret_id}", response_model=SecretDetailOut)
async def update_secret(secret_id: str, body: SecretUpdateIn, session: SessionDep) -> SecretDetailOut:
    secret = await service.update_secret(session, secret_id, body)
    metadata = body.metadata if body.metadata is not None else (await service.get_secret(session, secret_id))[2]
    return SecretDetailOut(**_summary(secret).model_dump(), value=None, metadata=metadata)


@router.delete("/secrets/{secret_id}", status_code=204)
async def delete_secret(secret_id: str, session: SessionDep) -> None:
    await service.delete_secret(session, secret_id)


@router.get("/secrets/{secret_id}/versions", response_model=list[SecretVersionOut])
async def list_versions(secret_id: str, session: SessionDep) -> list[SecretVersionOut]:
    versions = await service.list_versions(session, secret_id)
    return [SecretVersionOut(id=v.id, created_at=v.created_at) for v in versions]


@router.get("/secrets/{secret_id}/versions/{version_id}", response_model=SecretVersionValueOut)
async def reveal_version(secret_id: str, version_id: str, session: SessionDep) -> SecretVersionValueOut:
    version = await service.reveal_version(session, secret_id, version_id)
    return SecretVersionValueOut(id=version.id, value=service.decrypt_version_value(version), created_at=version.created_at)


@router.get("/folders", response_model=list[FolderOut])
async def list_folders(session: SessionDep) -> list[FolderOut]:
    return list(await service.list_folders(session))


@router.post("/folders", response_model=FolderOut, status_code=201)
async def create_folder(body: FolderIn, session: SessionDep) -> FolderOut:
    return await service.create_folder(session, body)


@router.delete("/folders/{folder_id}", status_code=204)
async def delete_folder(folder_id: str, session: SessionDep) -> None:
    await service.delete_folder(session, folder_id)


@router.get("/tags", response_model=list[TagOut])
async def list_tags(session: SessionDep) -> list[TagOut]:
    return list(await service.list_tags(session))


@router.post("/tags", response_model=TagOut, status_code=201)
async def create_tag(body: TagIn, session: SessionDep) -> TagOut:
    return await service.create_tag(session, body)


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: str, session: SessionDep) -> None:
    await service.delete_tag(session, tag_id)
