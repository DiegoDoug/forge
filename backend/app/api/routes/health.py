from __future__ import annotations

import shutil

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.version import VERSION

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/version")
async def version() -> dict:
    return {"name": "Forge", "version": VERSION}


@router.get("/system/status")
async def system_status() -> dict:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(settings.data_dir)
    db_size = settings.database_path.stat().st_size if settings.database_path.exists() else 0
    return {
        "version": VERSION,
        "environment": settings.environment,
        "storage": {
            "database_bytes": db_size,
            "disk_total_bytes": usage.total,
            "disk_used_bytes": usage.used,
            "disk_free_bytes": usage.free,
        },
    }
