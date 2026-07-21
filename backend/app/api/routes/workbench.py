from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep, SessionDep
from app.schemas.workbench import WorkbenchLayoutOut, WorkbenchLayoutUpdate, WorkbenchOut
from app.services import workbench as workbench_service

router = APIRouter(prefix="/workbench", tags=["workbench"], dependencies=[AuthDep])


@router.get("", response_model=WorkbenchOut)
async def get_workbench(session: SessionDep) -> WorkbenchOut:
    return WorkbenchOut(**await workbench_service.get_workbench(session))


@router.put("/layout", response_model=WorkbenchLayoutOut)
async def update_layout(body: WorkbenchLayoutUpdate, session: SessionDep) -> WorkbenchLayoutOut:
    layout = await workbench_service.update_layout(
        session,
        panels=[p.model_dump() for p in body.panels],
        pinned_tools=body.pinned_tools,
    )
    return WorkbenchLayoutOut(**workbench_service.serialize_layout(layout))


@router.post("/layout/reset", response_model=WorkbenchLayoutOut)
async def reset_layout(session: SessionDep) -> WorkbenchLayoutOut:
    layout = await workbench_service.reset_layout(session)
    return WorkbenchLayoutOut(**workbench_service.serialize_layout(layout))
