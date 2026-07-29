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
