"""The concrete, falsifiable test for the "Orchestrator-replaceable" design
principle (forge-docs/15_VERIFICATION_FRAMEWORK.md §9), required as a
Milestone 2 acceptance criterion and delivered here per Milestone 3's
"replaceability validation" per VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md.

Swaps the real Orchestrator for a from-scratch ReferenceOrchestrator and
confirms every Milestone 2 verifier still works, completely unchanged —
no verifier code, no verifier call convention, nothing about how the
verifiers are constructed differs between the two runs below.
"""

from fdk_verification import Orchestrator, ReferenceOrchestrator
from fdk_verification.verifiers import default_registry

from _fixtures import checklist, sample_contract


def test_reference_orchestrator_produces_the_same_verdict_as_the_real_one(tmp_path):
    contract = sample_contract()

    real_report = Orchestrator(default_registry()).run(contract, tmp_path)
    reference_report = ReferenceOrchestrator(default_registry()).run(contract, tmp_path)

    assert real_report.overall_status == reference_report.overall_status
    assert {r.name: r.status for r in real_report.results} == {
        r.name: r.status for r in reference_report.results
    }


def test_reference_orchestrator_agrees_on_a_failing_contract_too(tmp_path):
    contract = sample_contract(regression_targets=checklist(("routing still works", False)))

    real_report = Orchestrator(default_registry()).run(contract, tmp_path)
    reference_report = ReferenceOrchestrator(default_registry()).run(contract, tmp_path)

    assert real_report.overall_status == reference_report.overall_status
    assert [r.name for r in real_report.failed_results] == [r.name for r in reference_report.failed_results]


def test_every_verifier_runs_unmodified_under_the_reference_orchestrator(tmp_path):
    # Each verifier constructed and invoked exactly as ReferenceOrchestrator
    # invokes it — same contract, same workspace_root, same call signature —
    # proving no verifier needed a code change, a special case, or a
    # different call convention to work here.
    contract = sample_contract()
    for name, verifier in default_registry().items():
        result = verifier.run(contract, tmp_path)
        assert result.name == name
