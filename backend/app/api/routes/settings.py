from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.core.config import get_settings
from app.core.version import VERSION
from app.schemas.settings import AboutOut, BackupImportIn, BackupOut, ThemeIn
from app.services.settings import backup as backup_service
from app.services.settings import service as settings_service

router = APIRouter(prefix="/settings", tags=["settings"], dependencies=[AuthDep])


@router.get("/about", response_model=AboutOut)
async def about() -> AboutOut:
    settings = get_settings()
    return AboutOut(name="Forge", version=VERSION, environment=settings.environment)


@router.put("/theme")
async def update_theme(body: ThemeIn, session: SessionDep) -> dict:
    config = await settings_service.update_theme(session, body.theme)
    return {"theme": config.theme}


@router.get("/backup", response_model=BackupOut)
async def export_backup(session: SessionDep) -> BackupOut:
    return BackupOut(**await backup_service.export_backup(session))


@router.post("/backup/import")
async def import_backup(body: BackupImportIn, session: SessionDep) -> dict:
    return await backup_service.import_backup(session, body.model_dump())
