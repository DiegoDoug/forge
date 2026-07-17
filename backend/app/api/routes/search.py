from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.services.search import service

router = APIRouter(prefix="/search", tags=["search"], dependencies=[AuthDep])


@router.get("")
async def search(session: SessionDep, q: str = "") -> dict:
    return await service.global_search(session, q)
