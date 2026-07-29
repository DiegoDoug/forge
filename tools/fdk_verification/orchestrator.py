"""The Orchestrator skeleton (forge-docs/15_VERIFICATION_FRAMEWORK.md §3).

Milestone 1 scope: this coordinates whatever verifiers are registered
against a contract's declared requirements and aggregates their results.
It does not retry, repair, escalate, or auto-continue anything — that
behavior is Milestone 3 (repair loop) and Milestone 4 (FDK integration),
per forge-docs/templates/prompts/VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md.

Per §9's "Orchestrator-replaceable" principle: this class contains no
verifier-specific logic. It knows only the `Verifier` protocol's `run`
method and the verifier names a contract declares — never a specific
verifier's identity or behavior. A verifier that needed the orchestrator
to special-case it would violate that boundary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .contract import VerificationContract
from .report import VerificationReport, build_report
from .verifier import Verifier


class UnregisteredVerifierError(Exception):
    """A contract requires a verifier this Orchestrator instance doesn't have registered."""


class Orchestrator:
    def __init__(self, verifiers: Mapping[str, Verifier]):
        self._verifiers: dict[str, Verifier] = dict(verifiers)

    def run(
        self,
        contract: VerificationContract,
        workspace_root: Path,
        *,
        confidence: float | None = None,
    ) -> VerificationReport:
        """Run every verifier the contract requires, once, and aggregate the results.

        Raises UnregisteredVerifierError if the contract requires a
        verifier this Orchestrator wasn't given — an environment-level
        gap, distinct from `contract.validate_contract`'s check that a
        required verifier name is a *recognized* one at all.
        """
        results = []
        for name in sorted(contract.required_verifiers):
            verifier = self._verifiers.get(name)
            if verifier is None:
                raise UnregisteredVerifierError(
                    f"contract for phase {contract.phase_name!r} requires verifier {name!r}, "
                    f"but this Orchestrator has no verifier registered under that name "
                    f"(registered: {sorted(self._verifiers)})"
                )
            results.append(verifier.run(contract, workspace_root))

        return build_report(contract.phase_name, results, confidence=confidence)
