from pathlib import Path

from fdk_verification import VerifierStatus
from fdk_verification.verifiers import SpecificationVerifier


def test_passes_when_all_tasks_and_criteria_are_checked(make_contract, checklist):
    contract = make_contract(
        required_tasks=checklist(("T1: do the thing", True)),
        acceptance_criteria=checklist(("AC1: the thing works", True)),
    )

    result = SpecificationVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.PASS
    assert result.findings == []


def test_fails_and_names_every_unchecked_item(make_contract, checklist):
    contract = make_contract(
        required_tasks=checklist(("T1: done", True), ("T2: not done", False)),
        acceptance_criteria=checklist(("AC1: not verified", False)),
    )

    result = SpecificationVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.FAIL
    assert any("T2: not done" in f for f in result.findings)
    assert any("AC1: not verified" in f for f in result.findings)
    assert not any("T1: done" in f for f in result.findings)


def test_runs_independently_without_an_orchestrator(make_contract, checklist):
    # The independent-executability requirement, made explicit: no Orchestrator
    # object appears anywhere in this test.
    contract = make_contract(required_tasks=checklist(("T1", True)), acceptance_criteria=checklist(("AC1", True)))

    result = SpecificationVerifier().run(contract, Path("."))

    assert result.name == "Specification"
