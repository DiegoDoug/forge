from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    auth,
    converters,
    crypto,
    documents,
    generators,
    ingest,
    notes,
    project_init,
    search,
    secrets,
    settings,
    workbench,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(secrets.router, prefix="/secrets")
# Compatibility alias for the pre-rename path — proxies to the same handler,
# not a second implementation. See ADR-0006.
api_router.include_router(secrets.router, prefix="/vault")
api_router.include_router(generators.router)
api_router.include_router(crypto.router)
api_router.include_router(converters.router)
api_router.include_router(notes.router)
api_router.include_router(documents.router)
api_router.include_router(ingest.router)
api_router.include_router(search.router)
api_router.include_router(settings.router)
api_router.include_router(workbench.router)
api_router.include_router(project_init.router)
