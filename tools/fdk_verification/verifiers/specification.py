"""Specification Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.1).

Documented generic-tooling limitation: confirming that an arbitrary
acceptance criterion is actually true against a running app requires
app-specific knowledge this generic verifier doesn't have. What it can
check without that knowledge: whether every required task (§2) and
acceptance criterion (§3) the contract itself declares has been marked
complete. An unchecked item is treated as unfinished work — the only
signal available without bespoke per-criterion verification, and
consistent with forge-docs/12_BUG_CLASSIFICATION.md §2's framing that a
provably-false acceptance criterion is a BLOCKER.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus


class SpecificationVerifier:
    name = "Specification"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        findings = [
            f"required task not marked complete: {item.text}"
            for item in contract.required_tasks
            if not item.checked
        ]
        findings += [
            f"acceptance criterion not marked complete: {item.text}"
            for item in contract.acceptance_criteria
            if not item.checked
        ]
        status = VerifierStatus.FAIL if findings else VerifierStatus.PASS
        return VerifierResult(name=self.name, status=status, findings=findings)
