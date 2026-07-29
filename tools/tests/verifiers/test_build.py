import sys
from pathlib import Path

from fdk_verification import VerifierStatus
from fdk_verification.verifiers import BuildVerifier

_OK = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
_FAILS = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


def test_not_applicable_when_no_build_command_is_declared(make_contract):
    contract = make_contract(required_validation_commands=[])

    result = BuildVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.NOT_APPLICABLE


def test_passes_when_every_declared_build_command_succeeds(make_contract, checklist, tmp_path):
    contract = make_contract(
        required_validation_commands=checklist(
            (f"Lint: {_OK}", True),
            (f"Build: {_OK}", True),
        )
    )

    result = BuildVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.PASS


def test_fails_when_a_declared_build_command_exits_nonzero(make_contract, checklist, tmp_path):
    contract = make_contract(
        required_validation_commands=checklist(
            (f"Lint: {_OK}", True),
            (f"Typecheck: {_FAILS}", True),
        )
    )

    result = BuildVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.FAIL
    assert any("Typecheck" in f for f in result.findings)


def test_ignores_unchecked_and_test_labeled_commands(make_contract, checklist, tmp_path):
    contract = make_contract(
        required_validation_commands=checklist(
            (f"Build: {_FAILS}", False),  # declared but not required — must not run
            (f"Test: {_FAILS}", True),  # Test Verifier's domain, not Build's
        )
    )

    result = BuildVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.NOT_APPLICABLE
