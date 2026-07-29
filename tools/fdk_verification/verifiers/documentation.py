"""Documentation Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.7).

Generic scope: for each checked §7 item that names a concrete file path
(backticked, per VERIFICATION_CONTRACT_TEMPLATE.md's convention), confirms
that path appears among this workspace's changed files (via git) — a
real, checkable proxy for "this doc was actually touched." Items without
a parseable path are un-checkable by this generic verifier and are
reported as warnings, never silently treated as satisfied.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus
from ._git import changed_files
from ._paths import extract_path_tokens


class DocumentationVerifier:
    name = "Documentation"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        checked_items = [item for item in contract.documentation_requirements if item.checked]
        if not checked_items:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.NOT_APPLICABLE,
                warnings=["§7 Documentation Requirements declares no required updates"],
            )

        changed = changed_files(workspace_root)
        findings = []
        warnings = []
        for item in checked_items:
            tokens = extract_path_tokens(item.text)
            if not tokens:
                warnings.append(f"cannot verify (no parseable file path in requirement text): {item.text}")
                continue
            if not any(token in path for token in tokens for path in changed):
                findings.append(f"required documentation update not found among changed files: {item.text}")

        status = VerifierStatus.FAIL if findings else VerifierStatus.PASS
        return VerifierResult(name=self.name, status=status, findings=findings, warnings=warnings)
