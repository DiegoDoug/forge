from pathlib import Path

from fdk_verification import VerifierStatus
from fdk_verification.verifiers import UXVerifier


def test_always_not_applicable_regardless_of_contract_content(make_contract, checklist):
    contract = make_contract(acceptance_criteria=checklist(("dark mode looks right", False)))

    result = UXVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.NOT_APPLICABLE
    assert result.findings == []
    assert result.warnings, "must explain *why* it's N/A, not go silent about the gap"


def test_never_fails_even_on_an_otherwise_empty_contract(make_contract):
    contract = make_contract()

    result = UXVerifier().run(contract, Path("."))

    assert result.status is not VerifierStatus.FAIL
