"""The standard Verifier interface (forge-docs/15_VERIFICATION_FRAMEWORK.md §4, §9).

No concrete verifier lives here — that's Milestone 2. This module only
defines the boundary every verifier and the Orchestrator communicate
across, per the "Orchestrator-replaceable" design principle: the
Orchestrator must be able to invoke any object satisfying `Verifier`
without knowing anything verifier-specific.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from .contract import CANONICAL_VERIFIERS, VerificationContract
from .report import VerifierResult

__all__ = ["CANONICAL_VERIFIERS", "Verifier"]


@runtime_checkable
class Verifier(Protocol):
    """Anything a phase's Verification Contract can require by name.

    A verifier only evaluates — per §4's shared rule, nothing implementing
    this protocol may modify the codebase it is verifying. `run` must be
    independently callable outside an Orchestrator (for debugging and
    manual use, per §9's "Orchestrator-replaceable" principle) — it takes
    no orchestrator-specific state, only a contract and a workspace path.
    """

    name: str

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerifierResult: ...
