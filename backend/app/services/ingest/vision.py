"""Optional vision-LLM assist for image captioning and scanned-PDF transcription.

Ported from the standalone Ingest project. Disabled by default
(``FORGE_VISION_ENABLED=0``). All failures degrade gracefully to the plain
MarkItDown/pdfminer output — this module never turns a previously-working
conversion into an error.
"""

from __future__ import annotations

import base64
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger("forge.ingest.vision")

_PAGE_PROMPT = (
    "Transcribe this document page into clean Markdown. Preserve headings, "
    "reading order, lists, and tables (as Markdown tables). Transcribe all "
    "visible text verbatim. For non-text visuals (photos, charts, diagrams), "
    "add a brief bracketed description instead of transcribing them. Output "
    "only the Markdown for this page — no commentary, no code fences."
)

_client = None
_client_lock = threading.Lock()


def _semaphore() -> threading.Semaphore:
    return threading.Semaphore(max(1, get_settings().vision_max_concurrency))


def enabled() -> bool:
    settings = get_settings()
    return settings.vision_enabled and bool(settings.vision_api_key)


def get_llm_client():
    global _client
    if not enabled():
        return None
    if _client is None:
        with _client_lock:
            if _client is None:
                try:
                    from openai import OpenAI

                    settings = get_settings()
                    _client = OpenAI(
                        api_key=settings.vision_api_key,
                        base_url=settings.vision_base_url,
                        timeout=60.0,
                    )
                except Exception:
                    logger.exception("Failed to initialize vision LLM client")
                    return None
    return _client


def _caption_image_bytes(image_bytes: bytes, mime: str, prompt: str) -> str:
    client = get_llm_client()
    if client is None:
        raise RuntimeError("Vision client unavailable")
    settings = get_settings()
    b64 = base64.b64encode(image_bytes).decode("ascii")
    resp = client.chat.completions.create(
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ],
        max_tokens=4096,
    )
    return (resp.choices[0].message.content or "").strip()


def _page_count_and_sample_text(pdf_path: Path) -> tuple[int, list[str]]:
    import fitz  # PyMuPDF

    with fitz.open(pdf_path) as doc:
        return doc.page_count, [page.get_text() for page in doc]


def pdf_needs_vision(pdf_path: Path) -> tuple[bool, int]:
    settings = get_settings()
    if settings.vision_pdf_mode == "off" or not enabled():
        return False, 0
    try:
        page_count, page_texts = _page_count_and_sample_text(pdf_path)
    except Exception:
        logger.exception("Failed to inspect PDF %s for vision fallback", pdf_path)
        return False, 0

    if page_count == 0 or page_count > settings.vision_pdf_max_pages:
        return False, page_count

    if settings.vision_pdf_mode == "always":
        return True, page_count

    avg_chars = sum(len(t) for t in page_texts) / page_count
    return avg_chars < settings.vision_pdf_char_threshold, page_count


def convert_pdf_via_vision(pdf_path: Path) -> str:
    import fitz  # PyMuPDF

    settings = get_settings()
    zoom = settings.vision_pdf_dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as doc:
        page_images = [page.get_pixmap(matrix=matrix).tobytes("png") for page in doc]

    results: list[str | None] = [None] * len(page_images)
    errors: list[Exception] = []
    sem = _semaphore()

    def _do_page(i: int, img: bytes) -> None:
        try:
            with sem:
                results[i] = _caption_image_bytes(img, "image/png", _PAGE_PROMPT)
        except Exception as exc:
            errors.append(exc)

    with ThreadPoolExecutor(max_workers=settings.vision_max_concurrency) as pool:
        list(pool.map(lambda item: _do_page(*item), enumerate(page_images)))

    if errors:
        raise RuntimeError(f"Vision transcription failed for {len(errors)} page(s)") from errors[0]

    return "\n\n".join(text.strip() for text in results).strip() + "\n"
