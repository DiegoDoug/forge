import sys
from pathlib import Path

from fdk_verification import VerifierStatus
from fdk_verification.verifiers import TestVerifier

_OK = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
_FAILS = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


def test_not_applicable_when_no_test_command_is_declared(make_contract):
    contract = make_contract(required_validation_commands=[])

    result = TestVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.NOT_APPLICABLE


def test_passes_when_the_declared_test_command_succeeds(make_contract, checklist, tmp_path):
    contract = make_contract(required_validation_commands=checklist((f"Test: {_OK}", True)))

    result = TestVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.PASS


def test_fails_when_the_declared_test_command_exits_nonzero(make_contract, checklist, tmp_path):
    contract = make_contract(required_validation_commands=checklist((f"Test: {_FAILS}", True)))

    result = TestVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.FAIL
    assert any("Test" in f for f in result.findings)


def test_ignores_build_labeled_commands(make_contract, checklist, tmp_path):
    contract = make_contract(required_validation_commands=checklist((f"Build: {_FAILS}", True)))

    result = TestVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.NOT_APPLICABLE
