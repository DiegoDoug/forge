"""Build Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.3).

Delegates to whatever lint/typecheck/build/full-stack commands the
contract's §5 (Required Validation Commands) declares — this verifier
does not hardcode tsc/eslint/next build/docker by name; it only runs a
shell command and checks its exit code, per §9's Orchestrator-replaceable
principle applied one level down to the verifier itself.

Convention: a contract author labels each command, e.g.
"Lint: npm run lint" (see VERIFICATION_CONTRACT_TEMPLATE.md §5). Labels
containing "lint", "typecheck"/"type check", "build", "docker", or
"full-stack"/"full stack" (case-insensitive) are this verifier's domain;
"test"-labeled commands belong to the Test Verifier instead.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus
from ._commands import BUILD_LABEL_KEYWORDS, labeled_commands, run_labeled_commands


class BuildVerifier:
    name = "Build"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        commands = [
            (label, command)
            for label, command in labeled_commands(contract.required_validation_commands)
            if "test" not in label.lower() and any(keyword in label.lower() for keyword in BUILD_LABEL_KEYWORDS)
        ]
        if not commands:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.NOT_APPLICABLE,
                warnings=["no lint/typecheck/build/full-stack command declared and checked in §5 — nothing to verify"],
            )

        findings = run_labeled_commands(commands, workspace_root)
        status = VerifierStatus.FAIL if findings else VerifierStatus.PASS
        return VerifierResult(name=self.name, status=status, findings=findings)
