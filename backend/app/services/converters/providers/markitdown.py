"""Wraps the existing, unmodified Ingest pipeline as a `ConverterProvider`.

Universal Converter (Phase 04) Milestone 3. Per `03_BACKEND.md` §1-2, this is
a pure delegation adapter — `services/ingest/` itself is never modified or
re-implemented here, only referenced. `submit()` forwards directly to
`services.ingest.converter.submit`, with zero transformation of its own.

Importing this module registers `MarkItDownProvider` into the registry as a
side effect (`register(MarkItDownProvider())` below, run once at first
import). `app/api/routes/converters.py` is what triggers that import in the
running app, since it's the module that needs a real provider registered
before `GET /api/converters/providers` has anything to report.
"""

from __future__ import annotations

from app.services.ingest import converter, formats

from . import register


class MarkItDownProvider:
    slug = "markitdown"
    label = "Documents → Markdown"
    input_extensions = formats.KNOWN_EXTENSIONS
    output_format = "markdown"

    def submit(self, job) -> None:
        converter.submit(job)


register(MarkItDownProvider())
