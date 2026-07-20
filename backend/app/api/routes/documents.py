from __future__ import annotations

from fastapi import APIRouter, Response

from app.api.deps import AuthDep, SessionDep
from app.core.errors import AppError
from app.schemas.documents import DocumentCreateIn, DocumentOut, DocumentSummaryOut, DocumentUpdateIn
from app.services.documents import service
from app.services.documents.export import SUPPORTED_FORMATS, export_document

router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[AuthDep])


@router.get("", response_model=list[DocumentSummaryOut])
async def list_documents(session: SessionDep) -> list[DocumentSummaryOut]:
    return list(await service.list_documents(session))


@router.get("/search", response_model=list[DocumentSummaryOut])
async def search_documents(session: SessionDep, q: str) -> list[DocumentSummaryOut]:
    return list(await service.search_documents(session, q))


@router.post("", response_model=DocumentOut, status_code=201)
async def create_document(body: DocumentCreateIn, session: SessionDep) -> DocumentOut:
    return await service.create_document(session, body)


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: str, session: SessionDep) -> DocumentOut:
    return await service.get_document(session, document_id)


@router.patch("/{document_id}", response_model=DocumentOut)
async def update_document(document_id: str, body: DocumentUpdateIn, session: SessionDep) -> DocumentOut:
    return await service.update_document(session, document_id, body)


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str, session: SessionDep) -> None:
    await service.delete_document(session, document_id)


@router.get("/{document_id}/export")
async def export(document_id: str, session: SessionDep, format: str) -> Response:
    if format not in SUPPORTED_FORMATS:
        raise AppError(f"Unsupported export format: {format}. Choose one of {', '.join(SUPPORTED_FORMATS)}")
    document = await service.get_document(session, document_id)
    payload, media_type, filename = export_document(
        title=document.title,
        content=document.content,
        fmt=format,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
