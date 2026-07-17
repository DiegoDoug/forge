from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import auth, converters, crypto, dashboard, generators, ingest, notes, search, settings, vault

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(vault.router)
api_router.include_router(generators.router)
api_router.include_router(crypto.router)
api_router.include_router(converters.router)
api_router.include_router(notes.router)
api_router.include_router(ingest.router)
api_router.include_router(search.router)
api_router.include_router(dashboard.router)
api_router.include_router(settings.router)
