"""Shared test-only helpers for tools/tests/*.py (not part of fdk_verification itself).

Used by test files that live directly under tools/tests/ (integration,
replaceability, repair-loop, and escalation tests) — the per-verifier
unit tests under tools/tests/verifiers/ have their own, narrower
conftest.py fixtures and don't need this module.
"""

import sys

from fdk_verification import ChecklistItem, VerificationContract, VerifierResult, VerifierStatus, build_report

OK_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
FAILING_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


def checklist(*pairs):
    return [ChecklistItem(text=text, checked=checked) for text, checked in pairs]


def sample_contract(**overrides):
    defaults = dict(
        phase_name="05",
        phase_objective="",
        dependencies="",
        completion_definition="",
        required_tasks=checklist(("T1", True)),
        acceptance_criteria=checklist(("AC1", True)),
        expected_scope="",
        out_of_scope="",
        required_validation_commands=checklist(
            (f"Build: {OK_COMMAND}", True),
            (f"Test: {OK_COMMAND}", True),
        ),
        architecture_constraints=[],
        documentation_requirements=[],
        regression_targets=checklist(("routing still works", True)),
        verifier_declarations=checklist(
            ("Specification", True),
            ("Architecture", False),
            ("Build", True),
            ("Test", True),
            ("Regression", True),
            ("Code Quality", False),
            ("Documentation", False),
            ("UX — required", True),
        ),
    )
    defaults.update(overrides)
    return VerificationContract(**defaults)


def passing_report(phase_name="05", *, confidence=None, verifier_name="Build"):
    return build_report(
        phase_name,
        [VerifierResult(name=verifier_name, status=VerifierStatus.PASS)],
        confidence=confidence,
    )


def failing_report(phase_name="05", *, finding="something is broken", verifier_name="Build", confidence=None):
    return build_report(
        phase_name,
        [VerifierResult(name=verifier_name, status=VerifierStatus.FAIL, findings=[finding])],
        confidence=confidence,
    )
