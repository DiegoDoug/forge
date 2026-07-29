"""Orchestrator integration test using real, concrete verifiers (Milestone 2).

Distinct from test_orchestrator.py's Milestone 1 tests, which prove the
Orchestrator is generic using fakes. This proves the real
verifiers.default_registry() verifiers actually wire into the real
Orchestrator and produce a correct end-to-end PASS/FAIL decision.
"""

from fdk_verification import Orchestrator, OverallStatus, UnregisteredVerifierError
from fdk_verification.verifiers import default_registry

from _fixtures import checklist, sample_contract


def test_all_real_verifiers_pass_yields_overall_pass(tmp_path):
    contract = sample_contract()
    orchestrator = Orchestrator(default_registry())

    report = orchestrator.run(contract, tmp_path)

    assert report.overall_status is OverallStatus.PASS
    assert report.recommendation == "CONTINUE"
    result_by_name = {r.name: r.status.value for r in report.results}
    assert result_by_name == {
        "Specification": "PASS",
        "Build": "PASS",
        "Test": "PASS",
        "Regression": "PASS",
        "UX": "N/A",
    }


def test_a_single_real_verifier_failure_fails_the_whole_run(tmp_path):
    contract = sample_contract(regression_targets=checklist(("routing still works", False)))
    orchestrator = Orchestrator(default_registry())

    report = orchestrator.run(contract, tmp_path)

    assert report.overall_status is OverallStatus.FAIL
    assert report.recommendation == "REPAIR"
    assert [r.name for r in report.failed_results] == ["Regression"]


def test_orchestrator_refuses_to_run_with_a_verifier_missing_from_the_registry(tmp_path):
    contract = sample_contract()
    partial_registry = default_registry()
    del partial_registry["Regression"]
    orchestrator = Orchestrator(partial_registry)

    try:
        orchestrator.run(contract, tmp_path)
        assert False, "expected UnregisteredVerifierError"
    except UnregisteredVerifierError as exc:
        assert "Regression" in str(exc)
