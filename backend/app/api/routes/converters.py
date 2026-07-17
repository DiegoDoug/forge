from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep
from app.schemas.converters import CronParseIn, CronParseOut
from app.services.converters import cron

router = APIRouter(prefix="/converters", tags=["converters"], dependencies=[AuthDep])


@router.post("/cron/parse", response_model=CronParseOut)
async def parse_cron(body: CronParseIn) -> CronParseOut:
    return CronParseOut(**cron.parse_cron(body.expression, body.count))
