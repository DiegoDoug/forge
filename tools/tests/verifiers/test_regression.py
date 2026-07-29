from pathlib import Path

from fdk_verification import VerifierStatus
from fdk_verification.verifiers import RegressionVerifier


def test_not_applicable_when_contract_declares_no_targets(make_contract):
    contract = make_contract(regression_targets=[])

    result = RegressionVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.NOT_APPLICABLE


def test_passes_when_every_target_is_confirmed(make_contract, checklist):
    contract = make_contract(regression_targets=checklist(("routing still works", True)))

    result = RegressionVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.PASS


def test_fails_and_names_unconfirmed_targets(make_contract, checklist):
    contract = make_contract(
        regression_targets=checklist(
            ("routing still works", True),
            ("the JSON converter still round-trips", False),
        )
    )

    result = RegressionVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.FAIL
    assert any("JSON converter" in f for f in result.findings)
    assert not any("routing" in f for f in result.findings)
