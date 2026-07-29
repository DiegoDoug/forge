"""Regression Verifier (forge-docs/15_VERIFICATION_FRAMEWORK.md §4.5).

Documented generic-tooling limitation, same shape as the Specification
Verifier: confirming that arbitrary existing functionality (routing,
converters, shared components, ...) still works requires app-specific
test hooks this generic verifier doesn't have. What it can check: whether
every regression target the contract itself declares (§8) has been
confirmed by whoever ran the phase's regression pass. An unchecked target
is treated as unconfirmed, not silently assumed fine.
"""

from __future__ import annotations

from pathlib import Path

from ..contract import VerificationContract
from ..report import VerifierResult, VerifierStatus


class RegressionVerifier:
    name = "Regression"

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult:
        if not contract.regression_targets:
            return VerifierResult(
                name=self.name,
                status=VerifierStatus.NOT_APPLICABLE,
                warnings=["§8 Regression Targets declares no targets to check"],
            )

        findings = [
            f"regression target not confirmed: {item.text}"
            for item in contract.regression_targets
            if not item.checked
        ]
        status = VerifierStatus.FAIL if findings else VerifierStatus.PASS
        return VerifierResult(name=self.name, status=status, findings=findings)
