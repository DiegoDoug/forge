from pathlib import Path

from fdk_verification import Orchestrator, VerifierStatus
from fdk_verification.verifier import Verifier
from fdk_verification.verifiers import AgenticReviewVerifier, default_registry


def test_satisfies_the_verifier_protocol():
    assert isinstance(AgenticReviewVerifier(), Verifier)


def test_registered_under_its_canonical_name_in_the_default_registry():
    registry = default_registry()
    assert "Agentic Review" in registry
    assert isinstance(registry["Agentic Review"], AgenticReviewVerifier)


def test_orchestrator_can_run_it_like_any_other_verifier(tmp_path, make_contract, checklist):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    (reviews_dir / "AGENTIC_REVIEW.md").write_text("**Verdict:** PASS\n", encoding="utf-8")

    contract = make_contract(
        verifier_declarations=checklist(("Agentic Review", True)),
        source_path=contract_path,
    )
    orchestrator = Orchestrator({"Agentic Review": AgenticReviewVerifier()})

    report = orchestrator.run(contract, tmp_path)

    assert [r.name for r in report.results] == ["Agentic Review"]
    assert report.overall_status.value == "PASS"


def test_fails_when_no_review_artifact_exists(tmp_path, make_contract):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    contract = make_contract(source_path=contract_path)

    result = AgenticReviewVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.FAIL
    assert "no independent Agentic Review artifact found" in result.findings[0]


def test_fails_gracefully_when_contract_has_no_source_path(make_contract):
    contract = make_contract()  # source_path defaults to None

    result = AgenticReviewVerifier().run(contract, Path("."))

    assert result.status is VerifierStatus.FAIL
    assert result.findings


def test_passes_when_artifact_records_a_clean_pass_verdict(tmp_path, make_contract):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    (reviews_dir / "AGENTIC_REVIEW.md").write_text(
        "# Milestone Review\n\n**Verdict:** PASS\n\nNo blocking findings.\n", encoding="utf-8"
    )
    contract = make_contract(source_path=contract_path)

    result = AgenticReviewVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.PASS
    assert result.findings == []


def test_fails_and_preserves_verdict_text_when_not_a_clean_pass(tmp_path, make_contract):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    (reviews_dir / "AGENTIC_REVIEW.md").write_text(
        "**Verdict:** PASS WITH REQUIRED FIXES\n\n- fix the thing\n", encoding="utf-8"
    )
    contract = make_contract(source_path=contract_path)

    result = AgenticReviewVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.FAIL
    assert "PASS WITH REQUIRED FIXES" in result.findings[0]


def test_fails_when_artifact_has_no_parseable_verdict_line(tmp_path, make_contract):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    (reviews_dir / "AGENTIC_REVIEW.md").write_text("Some notes, no verdict recorded.\n", encoding="utf-8")
    contract = make_contract(source_path=contract_path)

    result = AgenticReviewVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.FAIL
    assert "no parseable" in result.findings[0]


def test_milestone_metadata_resolves_to_the_numbered_artifact_path(tmp_path, make_contract):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    # Only the M1-numbered file exists - proves the milestone metadata (not
    # the phase-wide fallback name) drives path resolution.
    (reviews_dir / "AGENTIC_REVIEW_M1.md").write_text("**Verdict:** PASS\n", encoding="utf-8")

    contract = make_contract(source_path=contract_path, milestone="Milestone 1 — MCP Foundation")

    result = AgenticReviewVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.PASS


def test_milestone_2_does_not_accidentally_read_milestone_1s_artifact(tmp_path, make_contract):
    contract_path = tmp_path / "VERIFICATION_CONTRACT.md"
    contract_path.write_text("placeholder", encoding="utf-8")
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    (reviews_dir / "AGENTIC_REVIEW_M1.md").write_text("**Verdict:** PASS\n", encoding="utf-8")

    contract = make_contract(source_path=contract_path, milestone="Milestone 2 — Knowledge CRUD")

    result = AgenticReviewVerifier().run(contract, tmp_path)

    assert result.status is VerifierStatus.FAIL
