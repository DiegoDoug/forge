from fdk_verification import VerifierStatus
from fdk_verification.verifiers import ArchitectureVerifier


def test_passes_with_a_warning_when_nothing_changed(make_contract, git_repo):
    contract = make_contract(out_of_scope="`backend/app/`")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert any("no changed files" in w for w in result.warnings)


def test_fails_when_a_changed_file_matches_an_out_of_scope_path(make_contract, git_repo):
    (git_repo / "backend").mkdir()
    (git_repo / "backend" / "app").mkdir()
    (git_repo / "backend" / "app" / "main.py").write_text("x = 1\n", encoding="utf-8")
    contract = make_contract(out_of_scope="`backend/app/`")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.FAIL
    assert any("backend/app" in f for f in result.findings)


def test_passes_when_changed_files_stay_in_scope(make_contract, git_repo):
    (git_repo / "tools").mkdir()
    (git_repo / "tools" / "fdk_verification.py").write_text("x = 1\n", encoding="utf-8")
    contract = make_contract(out_of_scope="`backend/app/`")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert result.findings == []


def test_warns_when_no_out_of_scope_is_declared(make_contract, git_repo):
    (git_repo / "anything.py").write_text("x = 1\n", encoding="utf-8")
    contract = make_contract(out_of_scope="")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert any("declares no explicit out-of-scope paths" in w for w in result.warnings)


def test_ignores_rc_generated_verification_reports_under_history(make_contract, git_repo):
    (git_repo / "forge-docs").mkdir()
    (git_repo / "forge-docs" / "history").mkdir()
    (git_repo / "forge-docs" / "history" / "2026-08-04-phase-07-verification-report.md").write_text(
        "report\n", encoding="utf-8"
    )
    (git_repo / "forge-docs" / "history" / "2026-08-04-phase-07-verification-escalation.md").write_text(
        "escalation\n", encoding="utf-8"
    )
    contract = make_contract(out_of_scope="`forge-docs/history/`")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert result.findings == []
    assert any("ignored one or more RC-pipeline-generated" in w for w in result.warnings)


def test_still_fails_on_legitimate_out_of_scope_history_edits(make_contract, git_repo):
    (git_repo / "forge-docs").mkdir()
    (git_repo / "forge-docs" / "history").mkdir()
    # A hand-written checkpoint-log entry — not the RC pipeline's generated
    # report/escalation naming pattern — must still be caught.
    (git_repo / "forge-docs" / "history" / "2026-08-04-phase-07-checkpoint-log.md").write_text(
        "manual entry\n", encoding="utf-8"
    )
    contract = make_contract(out_of_scope="`forge-docs/history/`")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.FAIL
    assert any("checkpoint-log" in f for f in result.findings)


def test_still_fails_when_generated_and_legitimate_history_changes_are_mixed(make_contract, git_repo):
    (git_repo / "forge-docs").mkdir()
    (git_repo / "forge-docs" / "history").mkdir()
    (git_repo / "forge-docs" / "history" / "2026-08-04-phase-07-verification-report.md").write_text(
        "report\n", encoding="utf-8"
    )
    (git_repo / "forge-docs" / "history" / "2026-08-04-phase-07-checkpoint-log.md").write_text(
        "manual entry\n", encoding="utf-8"
    )
    contract = make_contract(out_of_scope="`forge-docs/history/`")

    result = ArchitectureVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.FAIL
    assert any("checkpoint-log" in f for f in result.findings)
    assert not any("verification-report" in f for f in result.findings)
