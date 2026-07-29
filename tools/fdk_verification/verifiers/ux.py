"""UX Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.8, conditional).

Only invoked when a contract declares it required (§9). No browser
automation is available in this environment — Milestone 2 deliberately
adds no new dependency for one (Playwright/Selenium would be a new
external dependency requiring the ask-first process in
forge-docs/09_CLAUDE_CODE_RULES.md §3). UX criteria are therefore
structurally unverifiable by this generic verifier, which is exactly the
condition forge-docs/12_BUG_CLASSIFICATION.md §4 defines as an unverified
claim (track as a QA ticket) rather than a BLOCKER/MAJOR/MINOR finding —
so this verifier always reports NOT_APPLICABLE, never FAIL.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus


class UXVerifier:
    name = "UX"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        return VerifierResult(
            name=self.name,
            status=VerifierStatus.NOT_APPLICABLE,
            warnings=[
                "UX criteria are structurally unverifiable in this environment (no browser "
                "automation) — track manually as QA tickets per forge-docs/12_BUG_CLASSIFICATION.md §4"
            ],
        )
