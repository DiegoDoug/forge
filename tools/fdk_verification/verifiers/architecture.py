"""Architecture Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.2).

Documented generic-tooling scope: deep checks like circular imports or
duplicated service logic need language- and project-specific static
analysis this package doesn't implement in Milestone 2. What it does
check, generically: every file with an uncommitted change (via git)
stays within the contract's declared Expected File Scope (§4) — a real,
checkable subset of "architectural compliance," not the whole of it.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus
from ._generated_artifacts import is_rc_generated_artifact
from ._git import changed_files
from ._paths import extract_path_tokens

_SCOPE_LIMITATION_WARNING = (
    "deeper architectural checks (circular imports, duplicated services, layering) "
    "are out of this generic verifier's scope — see architecture.py's module docstring"
)


class ArchitectureVerifier:
    name = "Architecture"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        changed = changed_files(workspace_root)
        if not changed:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.PASS,
                warnings=[
                    "no changed files detected via git; nothing to check against Expected File Scope",
                    _SCOPE_LIMITATION_WARNING,
                ],
            )

        out_of_scope_tokens = extract_path_tokens(contract.out_of_scope)
        findings = [
            f"{path} matches declared out-of-scope path {token!r}"
            for path in changed
            for token in out_of_scope_tokens
            if path.startswith(token) and not is_rc_generated_artifact(path)
        ]

        warnings = [_SCOPE_LIMITATION_WARNING]
        if any(path.startswith(token) and is_rc_generated_artifact(path) for path in changed for token in out_of_scope_tokens):
            warnings.append(
                "ignored one or more RC-pipeline-generated verification/escalation reports under "
                "forge-docs/history/ — see _generated_artifacts.py"
            )
        if not out_of_scope_tokens:
            warnings.append("§4 Expected File Scope declares no explicit out-of-scope paths to check changed files against")

        status = VerifierStatus.FAIL if findings else VerifierStatus.PASS
        return VerifierResult(name=self.name, status=status, findings=findings, warnings=warnings)
