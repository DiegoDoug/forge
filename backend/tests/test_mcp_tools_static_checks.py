"""Static checks over app/mcp/**, not runtime behavior tests.

AC20 (08_ACCEPTANCE.md): no MCP tool handler may reach data via a raw ORM
call - every tool must go through a services/* function. Also confirms the
Secrets/Crypto/Settings import boundary (01_SPEC.md SS2) holds for the real,
complete set of tool modules, not just the Milestone 1 auth/server files
already covered by IMPLEMENT.md's Milestone 1 execution rules.

Broadened per the Milestone 2 Agentic Review (MINOR finding): the original
check used a narrow regex (only session.get/execute) and a non-recursive
glob (only app/mcp/tools/*.py, would miss a future subdirectory such as
Milestone 4's planned app/mcp/resources.py). Now scans every .py file under
app/mcp/ recursively and checks for the full set of common SQLAlchemy
AsyncSession data-access methods, not just two of them."""

from __future__ import annotations

import re
from pathlib import Path

MCP_DIR = Path(__file__).resolve().parent.parent / "app" / "mcp"

# The full set of AsyncSession methods that reach the database directly -
# any of these called on a variable named `session` inside app/mcp/**
# (outside the one legitimate exception below) is an ORM bypass; AC20
# requires every data access to go through a services/* function instead.
_ORM_BYPASS_RE = re.compile(r"\bsession\.(get|execute|scalar|scalars|exec|delete|merge|refresh)\s*\(")

# services/knowledge is a documented, narrow exception - forge_link_items/
# forge_unlink_items (Milestone 3) and the delete-sequence's
# purge_links_for/get_note-then-delete calls legitimately call
# knowledge_service functions directly, which is calling a services/*
# function, not bypassing one. This file only forbids the ORM being reached
# WITHOUT going through any services/* function at all.
_FORBIDDEN_IMPORTS = ("services.secrets", "services.crypto", "services.settings")

# Files that legitimately touch the ORM/session because their entire job is
# session plumbing, not domain data access - excluded from the ORM-bypass
# scan by design, not by oversight.
_SESSION_PLUMBING_FILES = {"_common.py"}


def _all_mcp_py_files() -> list[Path]:
    return sorted(MCP_DIR.rglob("*.py"))


def test_no_mcp_module_calls_the_orm_directly():
    offenders = []
    for path in _all_mcp_py_files():
        if path.name in _SESSION_PLUMBING_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        for match in _ORM_BYPASS_RE.finditer(text):
            offenders.append(f"{path.relative_to(MCP_DIR)}: {match.group(0)!r}")
    assert not offenders, f"ORM bypass found (AC20) - every tool must call a services/* function instead: {offenders}"


def test_no_mcp_module_imports_secrets_crypto_or_settings():
    offenders = []
    for path in _all_mcp_py_files():
        text = path.read_text(encoding="utf-8")
        for forbidden in _FORBIDDEN_IMPORTS:
            if forbidden in text:
                offenders.append(f"{path.relative_to(MCP_DIR)}: references {forbidden!r}")
    assert not offenders, f"Secrets/Crypto/Settings boundary violated (01_SPEC.md SS2): {offenders}"


def test_every_tool_module_has_a_register_function():
    for path in (MCP_DIR / "tools").glob("*.py"):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        assert "def register(server" in text, f"{path.name} is missing the register(server) convention"


def test_session_plumbing_exception_list_matches_reality():
    """Guards the exception list itself from silently growing stale - every
    file named in _SESSION_PLUMBING_FILES must actually exist, and this test
    documents why each one is there."""
    for name in _SESSION_PLUMBING_FILES:
        path = MCP_DIR / "tools" / name
        assert path.is_file(), f"{name} is listed as a session-plumbing exception but doesn't exist at {path}"
