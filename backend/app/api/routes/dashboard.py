from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[AuthDep])


@router.get("")
async def get_dashboard(session: SessionDep) -> dict:
    return await dashboard_service.get_dashboard(session)
