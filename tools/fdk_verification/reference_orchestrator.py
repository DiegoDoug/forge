"""The minimal reference Orchestrator — the concrete replaceability proof
for §9's "Orchestrator-replaceable" design principle.

Deliberately NOT the same implementation as orchestrator.Orchestrator:
different internal shape (a comprehension instead of a loop with an
early-exit lookup), a distinct exception type, no shared code or import
between this module and orchestrator.py at all. Same external contract:
takes a VerificationContract + workspace_root, returns a
VerificationReport built from whatever verifiers are registered.

If any of the 8 Milestone 2 verifiers needed a change to work here, the
replaceability principle would not actually be satisfied — see
tools/tests/test_replaceability.py for the test that proves they don't.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .contract import VerificationContract
from .report import VerificationReport, build_report
from .verifier import Verifier


class MissingVerifierError(Exception):
    """A contract requires a verifier this reference Orchestrator wasn't given.

    Intentionally a distinct type from orchestrator.UnregisteredVerifierError
    — the two Orchestrator implementations share no code, including error
    types, to keep this a genuine independent implementation rather than a
    thin subclass of the real one.
    """


class ReferenceOrchestrator:
    def __init__(self, verifiers: Mapping[str, Verifier]):
        self.verifiers = verifiers

    def run(self, contract: VerificationContract, workspace_root: Path) -> VerificationReport:
        missing = sorted(name for name in contract.required_verifiers if name not in self.verifiers)
        if missing:
            raise MissingVerifierError(f"reference orchestrator has no verifier registered for: {missing}")

        results = [
            self.verifiers[name].run(contract, workspace_root) for name in sorted(contract.required_verifiers)
        ]
        return build_report(contract.phase_name, results)
