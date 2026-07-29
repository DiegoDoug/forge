from pathlib import Path

import pytest

from fdk_verification import (
    Orchestrator,
    UnregisteredVerifierError,
    VerifierResult,
    VerifierStatus,
    parse_contract,
)

CONTRACT_TEXT = """\
## 1. Phase Metadata

- **Phase name:** 05

## 9. Required Verification Agents

- [x] Build
- [x] Test
- [ ] UX — not required
"""


class FakeVerifier:
    """A minimal stand-in satisfying the Verifier protocol structurally.

    Deliberately not one of the 8 canonical verifiers — the Orchestrator
    must not care. If any test here needed the Orchestrator to know a
    verifier's real name or purpose, that would be exactly the kind of
    verifier-specific logic §9's design principle forbids.
    """

    def __init__(self, name: str, status: VerifierStatus, findings=None):
        self.name = name
        self.status = status
        self.findings = findings or []
        self.call_count = 0

    def run(self, contract, workspace_root: Path) -> VerifierResult:
        self.call_count += 1
        return VerifierResult(name=self.name, status=self.status, findings=list(self.findings))


def test_orchestrator_runs_only_the_verifiers_the_contract_requires():
    contract = parse_contract(CONTRACT_TEXT)
    build = FakeVerifier("Build", VerifierStatus.PASS)
    test_ = FakeVerifier("Test", VerifierStatus.PASS)
    unused = FakeVerifier("Regression", VerifierStatus.FAIL)  # registered, but not required

    orchestrator = Orchestrator({"Build": build, "Test": test_, "Regression": unused})
    report = orchestrator.run(contract, Path("."))

    assert build.call_count == 1
    assert test_.call_count == 1
    assert unused.call_count == 0, "the orchestrator must not run verifiers the contract didn't require"
    assert {r.name for r in report.results} == {"Build", "Test"}


def test_orchestrator_raises_when_a_required_verifier_is_not_registered():
    contract = parse_contract(CONTRACT_TEXT)
    orchestrator = Orchestrator({"Build": FakeVerifier("Build", VerifierStatus.PASS)})

    with pytest.raises(UnregisteredVerifierError, match="Test"):
        orchestrator.run(contract, Path("."))


def test_orchestrator_is_generic_over_arbitrary_verifier_names():
    # No canonical-8 awareness anywhere in Orchestrator — proves §9's
    # "no verifier-specific logic" principle rather than merely asserting it.
    text = "## 1. Phase Metadata\n\n- **Phase name:** 05\n\n## 9. Required Verification Agents\n\n- [x] Anything\n"
    contract = parse_contract(text)
    orchestrator = Orchestrator({"Anything": FakeVerifier("Anything", VerifierStatus.PASS)})

    report = orchestrator.run(contract, Path("."))

    assert [r.name for r in report.results] == ["Anything"]


def test_orchestrator_aggregates_into_the_report_model():
    contract = parse_contract(CONTRACT_TEXT)
    orchestrator = Orchestrator(
        {
            "Build": FakeVerifier("Build", VerifierStatus.PASS),
            "Test": FakeVerifier("Test", VerifierStatus.FAIL, findings=["one test failing"]),
        }
    )

    report = orchestrator.run(contract, Path("."), confidence=0.8)

    assert report.phase_name == "05"
    assert report.overall_status.value == "FAIL"
    assert report.confidence == 0.8
