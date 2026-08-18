"""Agentic Review Verifier (Phase 11 / Claude MCP / Second Brain, Milestone 1).

Every other verifier in this package is purely mechanical - git diff/status,
checkbox parsing, shell exit codes, regex marker scans. None of them can
independently judge whether an implementation is *correct* against a
milestone's spec, only whether declared checklist items are checked off or a
command exited zero. Phase 11's milestone gates require exactly the kind of
independent judgment those verifiers cannot provide - see
forge-docs/implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md §0.

This module deliberately does NOT invoke an LLM itself. A plain Python
module running under pytest has no access to the Agent/Workflow tools an
orchestrating Claude Code session has - only that outer session can spawn an
independent review. This mirrors RepairLoop's own design (`on_remediation`
is a notification hook for "an external mechanism... eventually" to act on,
never something RepairLoop does itself): the Claude Code session performs
the actual independent review and writes its structured verdict to a
well-known artifact path; this verifier's job is to require that artifact
exist, be well-formed, and be a genuine PASS before the milestone gate can
report PASS - the same "evaluates, never modifies" boundary the Verifier
protocol already requires of every other verifier here.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus

_VERDICT_RE = re.compile(r"^\*\*Verdict:\*\*\s*(.+?)\s*$", re.MULTILINE)
_MILESTONE_NUMBER_RE = re.compile(r"(\d+)")

# PASS WITH REQUIRED FIXES is a valid verdict a reviewer can write, but the
# underlying VerifierStatus enum is binary (PASS/FAIL/N-A - no
# PASS_WITH_FIXES member exists in report.py). Per the documented mapping in
# 09_IMPLEMENTATION_TASKS.md §0 point 3: anything short of a clean PASS maps
# to FAIL at the machine-readable level, with the reviewer's actual verdict
# text preserved verbatim in findings so "needs fixes, not a hard failure"
# is still visible to whoever reads the rendered report.
_PASS_VERDICTS = {"PASS"}


def _artifact_path(contract: VerificationContract, workspace_root: Path) -> Path | None:
    if contract.source_path is None:
        return None
    reviews_dir = contract.source_path.parent / "reviews"
    match = _MILESTONE_NUMBER_RE.search(contract.milestone)
    if match:
        return reviews_dir / f"AGENTIC_REVIEW_M{match.group(1)}.md"
    return reviews_dir / "AGENTIC_REVIEW.md"


class AgenticReviewVerifier:
    name = "Agentic Review"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        path = _artifact_path(contract, workspace_root)
        if path is None:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.FAIL,
                findings=[
                    "no independent Agentic Review has been recorded (contract has no "
                    "source_path, so no reviews/ artifact location could be determined)"
                ],
            )

        if not path.is_file():
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.FAIL,
                findings=[
                    f"no independent Agentic Review artifact found at {path} - this milestone "
                    "cannot be declared complete until an independent review has been run and "
                    "its verdict recorded there (never self-declared by the implementing session)"
                ],
            )

        text = path.read_text(encoding="utf-8")
        match = _VERDICT_RE.search(text)
        if match is None:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.FAIL,
                findings=[f"{path} exists but has no parseable '**Verdict:** ...' line"],
            )

        verdict = match.group(1).strip()
        if verdict.upper() in _PASS_VERDICTS:
            return VerifierResult(name=self.name, status=VerifierStatus.PASS, findings=[])

        return VerifierResult(
            name=self.name,
            status=VerifierStatus.FAIL,
            findings=[f"independent Agentic Review verdict was {verdict!r}, not PASS (see {path})"],
        )
