"""Path-token extraction from contract prose, shared by Architecture and Documentation.

Contract authors write file scope and doc-requirement text as free-form
Markdown (see VERIFICATION_CONTRACT_TEMPLATE.md §4, §7), typically with
backticked paths. This is a best-effort heuristic, not a parser for an
enforced grammar — documented as a known limitation wherever it's used.
"""

from __future__ import annotations

import re

_BACKTICKED_RE = re.compile(r"`([^`]+)`")
_EXTENSION_RE = re.compile(r"^[\w.\-/]+\.[A-Za-z0-9]{1,5}$")


def _looks_like_path(token: str) -> bool:
    # Free text ("Update the relevant docs somewhere") must never be
    # mistaken for a path — the space check alone rejects any real prose,
    # while still accepting a bare, non-backticked path or filename.
    if " " in token:
        return False
    return "/" in token or bool(_EXTENSION_RE.match(token))


def extract_path_tokens(text: str) -> list[str]:
    backticked = _BACKTICKED_RE.findall(text)
    if backticked:
        return [token.strip() for token in backticked if token.strip()]
    if not text.strip():
        return []
    candidates = [token.strip() for token in text.split(",") if token.strip()]
    return [token for token in candidates if _looks_like_path(token)]
