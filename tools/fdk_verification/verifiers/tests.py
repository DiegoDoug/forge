"""Test Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.4).

Delegates to whatever test command(s) the contract's §5 declares, labeled
"test" (case-insensitive) and not also a build/lint/typecheck/docker
label — avoids double-running an item that legitimately belongs to the
Build Verifier instead. Does not parse test-runner output for skip/
snapshot-regression detail (that's tool-specific and out of Milestone 2's
generic scope) — only the exit code decides PASS/FAIL, per §4.3's build
convention applied here too.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus
from ._commands import BUILD_LABEL_KEYWORDS, labeled_commands, run_labeled_commands


class TestVerifier:
    name = "Test"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        commands = [
            (label, command)
            for label, command in labeled_commands(contract.required_validation_commands)
            if "test" in label.lower() and not any(keyword in label.lower() for keyword in BUILD_LABEL_KEYWORDS)
        ]
        if not commands:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.NOT_APPLICABLE,
                warnings=["no test command declared and checked in §5 — nothing to verify"],
            )

        findings = run_labeled_commands(commands, workspace_root)
        status = VerifierStatus.FAIL if findings else VerifierStatus.PASS
        return VerifierResult(name=self.name, status=status, findings=findings)
