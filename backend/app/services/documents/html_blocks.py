from __future__ import annotations

import re

from bs4 import BeautifulSoup, NavigableString, Tag

BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "blockquote"}
_ALIGN_RE = re.compile(r"text-align:\s*(left|center|right|justify)")
_SIZE_PX_RE = re.compile(r"font-size:\s*([\d.]+)px")
_SIZE_PT_RE = re.compile(r"font-size:\s*([\d.]+)pt")
_FAMILY_RE = re.compile(r"font-family:\s*([^;]+)")

_EMPTY_FMT = {"bold": False, "italic": False, "underline": False, "strike": False, "font": None, "size": None}


def _block_align(tag: Tag) -> str:
    style = tag.get("style") or ""
    m = _ALIGN_RE.search(style)
    return m.group(1) if m else "left"


def _font_size_pt(tag: Tag) -> float | None:
    style = tag.get("style") or ""
    if tag.name == "font" and tag.get("size"):
        # legacy HTML font size="1..7" — map roughly onto a pt scale.
        legacy = {"1": 8, "2": 10, "3": 12, "4": 14, "5": 18, "6": 24, "7": 32}
        if tag["size"] in legacy:
            return float(legacy[tag["size"]])
    m = _SIZE_PX_RE.search(style)
    if m:
        return round(float(m.group(1)) * 0.75, 1)
    m = _SIZE_PT_RE.search(style)
    if m:
        return float(m.group(1))
    return None


def _font_family(tag: Tag) -> str | None:
    if tag.name == "font" and tag.get("face"):
        return tag["face"].split(",")[0].strip().strip("'\"")
    style = tag.get("style") or ""
    m = _FAMILY_RE.search(style)
    if m:
        return m.group(1).strip().strip("'\"").split(",")[0].strip()
    return None


def _walk_runs(node: Tag, fmt: dict) -> list[dict]:
    runs: list[dict] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if text:
                runs.append({**fmt, "text": text})
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name == "br":
            runs.append({**fmt, "text": "\n"})
            continue
        if name == "script" or name == "style":
            continue
        new_fmt = dict(fmt)
        if name in ("b", "strong"):
            new_fmt["bold"] = True
        elif name in ("i", "em"):
            new_fmt["italic"] = True
        elif name == "u":
            new_fmt["underline"] = True
        elif name in ("s", "strike", "del"):
            new_fmt["strike"] = True
        family = _font_family(child)
        if family:
            new_fmt["font"] = family
        size = _font_size_pt(child)
        if size:
            new_fmt["size"] = size
        runs.extend(_walk_runs(child, new_fmt))
    return runs


def _emit_block(blocks: list[dict], tag: Tag, type_: str, *, level: int | None = None, ordered: bool | None = None, index: int | None = None) -> None:
    runs = _walk_runs(tag, dict(_EMPTY_FMT))
    if not runs:
        runs = [{**_EMPTY_FMT, "text": ""}]
    blocks.append(
        {"type": type_, "level": level, "align": _block_align(tag), "ordered": ordered, "index": index, "runs": runs}
    )


def parse_blocks(html: str) -> list[dict]:
    """Parses editor HTML into a flat list of block dicts (paragraph / heading
    / list_item), each carrying an ordered list of formatted text runs. Shared
    by every export format except Markdown (which uses ``markdownify`` on the
    raw HTML directly, since it already understands this structure)."""

    soup = BeautifulSoup(html or "", "html.parser")
    blocks: list[dict] = []

    root_children = list(soup.children)
    has_block = any(isinstance(c, Tag) and c.name.lower() in BLOCK_TAGS for c in root_children)

    if not has_block:
        if soup.get_text(strip=True) == "" and not soup.find("br"):
            return []
        _emit_block(blocks, soup, "paragraph")
        return blocks

    for child in root_children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                blocks.append({"type": "paragraph", "level": None, "align": "left", "ordered": None, "index": None, "runs": [{**_EMPTY_FMT, "text": text}]})
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name in ("ul", "ol"):
            ordered = name == "ol"
            for i, li in enumerate(child.find_all("li", recursive=False), start=1):
                _emit_block(blocks, li, "list_item", ordered=ordered, index=i)
        elif name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            _emit_block(blocks, child, "heading", level=int(name[1]))
        elif name in ("p", "div", "blockquote"):
            _emit_block(blocks, child, "paragraph")
        else:
            _emit_block(blocks, child, "paragraph")

    return blocks
