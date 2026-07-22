from __future__ import annotations

from fastapi import APIRouter, Response

from app.api.deps import AuthDep, SessionDep
from app.schemas.project_init import GenerateRequest, GenerationListOut, GenerationOut, TemplateCatalogOut
from app.services.project_init import service
from app.services.project_init.catalog import get_catalog

router = APIRouter(prefix="/project-init", tags=["project-init"], dependencies=[AuthDep])


@router.get("/catalog", response_model=TemplateCatalogOut)
async def catalog() -> TemplateCatalogOut:
    return get_catalog()


@router.post("/generate", response_model=GenerationOut, status_code=201)
async def generate(body: GenerateRequest, session: SessionDep) -> GenerationOut:
    record, files = await service.generate(session, body.kind, body.config)
    return GenerationOut(
        id=record.id, kind=record.kind, name=record.name, created_at=record.created_at, file_count=len(files)
    )


@router.get("/history", response_model=GenerationListOut)
async def history(session: SessionDep, limit: int = service.HISTORY_LIMIT_DEFAULT) -> GenerationListOut:
    records = await service.list_history(session, limit=limit)
    return GenerationListOut(items=list(records))


@router.get("/{generation_id}/download")
async def download(generation_id: str, session: SessionDep) -> Response:
    _record, zip_bytes, filename = await service.render_zip_for(session, generation_id)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{generation_id}", status_code=204)
async def delete(generation_id: str, session: SessionDep) -> None:
    await service.delete(session, generation_id)
