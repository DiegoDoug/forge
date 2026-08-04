"""Code Quality Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.6).

Scans changed files (via git) for stray TODO/FIXME markers and a small,
non-exhaustive set of likely debug-statement patterns. Always reported as
warnings, never a FAIL — per §4.6: "may recommend improvements but should
fail only when quality issues violate project standards." This generic
verifier has no project-specific standards definition to fail against, so
it never manufactures a BLOCKER-level failure for a stylistic finding.

TODO/FIXME detection requires the conventional marker form — `TODO:`,
`TODO(name):`, `FIXME:`, `FIXME(name):` — rather than a bare substring
match, so prose that merely contains the word ("a section titled TODO",
ADR template boilerplate, this module's own docstring) isn't flagged.
This is still a heuristic, not a comment-syntax-aware parser: a marker
inside a string literal that happens to use this exact form would still
be (correctly, if noisily) flagged, same as any real TODO scanner.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus
from ._git import changed_files

_MARKER_RE = re.compile(r"\b(TODO|FIXME)\b(\([^)]*\))?\s*:")
_DEBUG_PATTERNS = ("console.log(", "debugger;", "print(")


class CodeQualityVerifier:
    name = "Code Quality"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        warnings = []
        for rel_path in changed_files(workspace_root):
            path = workspace_root / rel_path
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if _MARKER_RE.search(line):
                    warnings.append(f"{rel_path}:{lineno}: stray TODO/FIXME marker")
                if any(pattern in line for pattern in _DEBUG_PATTERNS):
                    warnings.append(f"{rel_path}:{lineno}: possible debug statement")

        return VerifierResult(name=self.name, status=VerifierStatus.PASS, warnings=warnings)
