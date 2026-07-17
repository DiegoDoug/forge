from __future__ import annotations

import io
import re
import uuid
import zipfile

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.api.deps import AuthDep, SessionDep
from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError
from app.models.activity import ActivityAction
from app.schemas.notes import NoteOut
from app.services import activity
from app.services.ingest import converter
from app.services.ingest.formats import KNOWN_EXTENSIONS
from app.services.ingest.jobs import FileTask, Job, store
from app.services.notes import service as notes_service
from app.schemas.notes import NoteCreateIn

router = APIRouter(prefix="/ingest", tags=["ingest"], dependencies=[AuthDep])

_UNSAFE = re.compile(r"[^A-Za-z0-9._ -]+")


def _safe_name(name: str) -> str:
    from pathlib import Path

    name = Path(name).name
    name = _UNSAFE.sub("_", name).strip(" .") or "file"
    return name[:150]


def _md_name(original: str) -> str:
    stem = original.rsplit(".", 1)[0] if "." in original else original
    return f"{stem}.md"


def _task_view(job: Job, task: FileTask) -> dict:
    return {
        "id": task.id,
        "name": task.original_name,
        "markdown_name": _md_name(task.original_name),
        "status": task.status,
        "error": task.error,
        "output_size": task.output_size,
        "used_vision": task.used_vision,
        "download_url": f"/api/ingest/jobs/{job.id}/files/{task.id}/download" if task.status == "done" else None,
    }


def _job_view(job: Job) -> dict:
    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "files": [_task_view(job, t) for t in job.files],
        "download_all_url": f"/api/ingest/jobs/{job.id}/download"
        if job.status in ("done", "failed") and any(t.status == "done" for t in job.files)
        else None,
    }


@router.get("/formats")
async def formats() -> dict:
    return {"extensions": sorted(KNOWN_EXTENSIONS)}


@router.post("/jobs", status_code=202)
async def create_job(files: list[UploadFile], session: SessionDep) -> dict:
    settings = get_settings()
    if not files:
        raise AppError("No files uploaded")
    if len(files) > settings.max_upload_batch_files:
        raise AppError(f"Too many files (max {settings.max_upload_batch_files} per batch)")

    store.start_cleanup_thread()
    job = store.create()
    max_bytes = settings.max_upload_file_size_mb * 1024 * 1024
    for upload in files:
        original = _safe_name(upload.filename or "file")
        task = FileTask(
            id=uuid.uuid4().hex[:12],
            original_name=original,
            upload_path=job.dir() / "in" / f"{uuid.uuid4().hex[:12]}-{original}",
        )

        size = 0
        too_big = False
        with task.upload_path.open("wb") as fh:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    too_big = True
                    break
                fh.write(chunk)

        if too_big:
            task.upload_path.unlink(missing_ok=True)
            task.status = "error"
            task.error = f"File exceeds the {settings.max_upload_file_size_mb} MB limit"
        elif size == 0:
            task.upload_path.unlink(missing_ok=True)
            task.status = "error"
            task.error = "File is empty"
        job.files.append(task)

    converter.submit(job)
    activity.record(session, ActivityAction.converted, "ingest_job", job.id, f"Converting {len(job.files)} file(s)")
    await session.commit()
    return _job_view(job)


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    job = store.get(job_id)
    if job is None:
        raise NotFoundError("Job not found or expired")
    return _job_view(job)


@router.get("/jobs/{job_id}/files/{file_id}/download")
async def download_file(job_id: str, file_id: str) -> FileResponse:
    job = store.get(job_id)
    if job is None:
        raise NotFoundError("Job not found or expired")
    task = next((t for t in job.files if t.id == file_id), None)
    if task is None or task.status != "done" or task.output_path is None:
        raise NotFoundError("Converted file not available")
    return FileResponse(task.output_path, media_type="text/markdown; charset=utf-8", filename=_md_name(task.original_name))


@router.get("/jobs/{job_id}/files/{file_id}/content")
async def file_content(job_id: str, file_id: str) -> dict:
    job = store.get(job_id)
    if job is None:
        raise NotFoundError("Job not found or expired")
    task = next((t for t in job.files if t.id == file_id), None)
    if task is None or task.status != "done" or task.output_path is None:
        raise NotFoundError("Converted file not available")
    return {"name": _md_name(task.original_name), "markdown": task.output_path.read_text("utf-8")}


@router.get("/jobs/{job_id}/download")
async def download_all(job_id: str) -> StreamingResponse:
    job = store.get(job_id)
    if job is None:
        raise NotFoundError("Job not found or expired")
    done = [t for t in job.files if t.status == "done" and t.output_path]
    if not done:
        raise NotFoundError("No converted files available")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        used: set[str] = set()
        for task in done:
            name = _md_name(task.original_name)
            if name in used:
                name = f"{name[:-3]}-{task.id}.md"
            used.add(name)
            zf.write(task.output_path, arcname=name)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="markdown-{job.id[:8]}.zip"'},
    )


class SaveToNoteIn(BaseModel):
    color: str = "#fde68a"


@router.post("/jobs/{job_id}/files/{file_id}/save-to-notes", response_model=NoteOut, status_code=201)
async def save_to_notes(job_id: str, file_id: str, body: SaveToNoteIn, session: SessionDep) -> NoteOut:
    job = store.get(job_id)
    if job is None:
        raise NotFoundError("Job not found or expired")
    task = next((t for t in job.files if t.id == file_id), None)
    if task is None or task.status != "done" or task.output_path is None:
        raise NotFoundError("Converted file not available")

    markdown = task.output_path.read_text("utf-8")
    note = await notes_service.create_note(
        session,
        NoteCreateIn(title=_md_name(task.original_name).removesuffix(".md"), content=markdown, color=body.color),
    )
    return note
