from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep
from app.schemas.converters import CronParseIn, CronParseOut, ProviderOut, ProvidersOut
from app.services.converters import cron, providers
from app.services.converters.providers import markitdown  # noqa: F401 -- registers MarkItDownProvider on import

router = APIRouter(prefix="/converters", tags=["converters"], dependencies=[AuthDep])


@router.post("/cron/parse", response_model=CronParseOut)
async def parse_cron(body: CronParseIn) -> CronParseOut:
    return CronParseOut(**cron.parse_cron(body.expression, body.count))


@router.get("/providers", response_model=ProvidersOut)
async def get_providers() -> ProvidersOut:
    return ProvidersOut(
        providers=[
            ProviderOut(
                slug=p.slug,
                label=p.label,
                input_extensions=sorted(p.input_extensions),
                output_format=p.output_format,
            )
            for p in providers.list_providers()
        ]
    )
