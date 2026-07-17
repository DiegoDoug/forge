"""Runs MarkItDown conversions on a worker pool.

Ported from the standalone Ingest project (github.com/DiegoDoug/Ingest);
job/file bookkeeping now flows through Forge's shared job store and
settings instead of the standalone app's own config module.
"""

from __future__ import annotations

import base64
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from markitdown import MarkItDown
from markitdown.converters import PptxConverter

from app.core.config import get_settings

from . import vision
from .jobs import FileTask, Job
from .postprocess import clean_markdown

logger = logging.getLogger("forge.ingest.converter")

_executor: ThreadPoolExecutor | None = None
_local = threading.local()


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(
            max_workers=get_settings().ingest_workers, thread_name_prefix="ingest-convert"
        )
    return _executor


def _patch_pptx_converter() -> None:
    """Work around a MarkItDown bug: python-pptx raises ValueError (not
    AttributeError) from the `.image` property of a picture placeholder
    that has no picture inserted into it. MarkItDown's `_is_picture` uses
    `hasattr(shape, "image")`, and hasattr only swallows AttributeError, so
    that ValueError propagates and aborts the whole PPTX conversion.
    """

    def _is_picture(self, shape):
        import pptx

        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
            return True
        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PLACEHOLDER:
            try:
                return hasattr(shape, "image")
            except ValueError:
                return False
        return False

    PptxConverter._is_picture = _is_picture


_patch_pptx_converter()


def _markitdown() -> MarkItDown:
    md = getattr(_local, "md", None)
    if md is None:
        llm_client = vision.get_llm_client()
        settings = get_settings()
        md = MarkItDown(
            enable_plugins=False,
            llm_client=llm_client,
            llm_model=settings.vision_model if llm_client else None,
        )
        _local.md = md
    return md


def _convert_pdf(task: FileTask) -> str | None:
    use_vision, _ = vision.pdf_needs_vision(task.upload_path)
    if not use_vision:
        return None
    try:
        markdown = vision.convert_pdf_via_vision(task.upload_path)
        task.used_vision = True
        return markdown
    except Exception:
        logger.exception("Vision PDF conversion failed for %s, falling back", task.original_name)
        return None


def _pdf_image_placeholder_fallback(pdf_path: Path) -> str:
    import fitz  # PyMuPDF

    zoom = get_settings().vision_pdf_dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    parts = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            png = page.get_pixmap(matrix=matrix).tobytes("png")
            b64 = base64.b64encode(png).decode("ascii")
            parts.append(f"![Page {i}](data:image/png;base64,{b64})")
    return "\n\n".join(parts) + "\n"


def _convert_one(job: Job, task: FileTask) -> None:
    task.status = "processing"
    try:
        markdown = None
        if task.upload_path.suffix.lower() == ".pdf":
            markdown = _convert_pdf(task)

        if markdown is None:
            result = _markitdown().convert(str(task.upload_path))
            markdown = result.text_content or ""

        markdown = clean_markdown(markdown)
        if not markdown and task.upload_path.suffix.lower() == ".pdf":
            try:
                markdown = clean_markdown(_pdf_image_placeholder_fallback(task.upload_path))
            except Exception:
                logger.exception("PDF image placeholder fallback failed for %s", task.original_name)

        if not markdown:
            raise ValueError("Conversion produced no text content")

        out_path = job.dir() / "out" / f"{task.id}.md"
        out_path.write_text(markdown, encoding="utf-8")

        task.output_path = out_path
        task.output_size = out_path.stat().st_size
        task.status = "done"
    except Exception as exc:
        logger.exception("Conversion failed for %s", task.original_name)
        task.status = "error"
        if type(exc).__name__ == "UnsupportedFormatException":
            task.error = "This file type is not supported."
        else:
            task.error = f"{type(exc).__name__}: {exc}"
    finally:
        task.upload_path.unlink(missing_ok=True)


def submit(job: Job) -> None:
    for task in job.files:
        if task.status == "pending":
            _get_executor().submit(_convert_one, job, task)
