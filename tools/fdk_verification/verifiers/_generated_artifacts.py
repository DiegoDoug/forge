"""Recognizes RC-pipeline-generated verification artifacts by filename.

`pipeline.py::persist_reports` writes exactly two kinds of file, always
under `forge-docs/history/`, always named
`<ISO-date>-phase-<number>-verification-report.md` or
`...-verification-escalation.md` (see `pipeline.py`'s `_report_document`/
`_escalation_document` and their call sites). That naming convention is
the pipeline's own contract with itself — not phase-specific, not
contract-specific — so it is safe to recognize generically here.

This exists to let the Architecture Verifier distinguish "the RC pipeline
just wrote down its own results" from "someone changed a file under a
declared out-of-scope path" without weakening out-of-scope protection for
`forge-docs/history/` in general: a hand-edited or pre-existing history
file that doesn't match this exact naming pattern is still caught.
"""

from __future__ import annotations

import re

_GENERATED_REPORT_RE = re.compile(
    r"^forge-docs/history/\d{4}-\d{2}-\d{2}-phase-[^/]+-verification-(report|escalation)\.md$"
)


def is_rc_generated_artifact(path: str) -> bool:
    return bool(_GENERATED_REPORT_RE.match(path.replace("\\", "/")))
