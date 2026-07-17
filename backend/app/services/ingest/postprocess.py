"""Cleanup of MarkItDown output for LLM / RAG consumption.

Ported from the standalone Ingest project (github.com/DiegoDoug/Ingest),
unchanged: preserve structure (headings, tables, lists, code blocks) while
stripping characters and repetition that only cost tokens.
"""

from __future__ import annotations

import re

_INVISIBLE = re.compile("[​‌‍⁠﻿­]")

_CHAR_MAP = {
    " ": " ",
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "–": "-", "—": " - ",
    "…": "...",
}

_DATA_URI_IMAGE = re.compile(r"!\[([^\]]*)\]\(data:[^)]{64,}\)")


def clean_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _INVISIBLE.sub("", text)
    for src, dst in _CHAR_MAP.items():
        text = text.replace(src, dst)

    text = _DATA_URI_IMAGE.sub(lambda m: f"![{m.group(1)}](embedded-image)", text)

    out: list[str] = []
    blank_run = 0
    in_code = False
    for line in text.split("\n"):
        stripped = line.rstrip()
        if stripped.lstrip().startswith("```"):
            in_code = not in_code
        if in_code:
            out.append(line)
            blank_run = 0
            continue
        if stripped == "":
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        out.append(stripped)

    result = "\n".join(out).strip()
    return result + "\n" if result else ""
