from fdk_verification import VerifierStatus
from fdk_verification.verifiers import CodeQualityVerifier


def test_passes_with_no_warnings_when_nothing_changed(make_contract, git_repo):
    contract = make_contract()

    result = CodeQualityVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert result.warnings == []


def test_never_fails_but_warns_on_todo_and_debug_statements(make_contract, git_repo):
    (git_repo / "module.py").write_text(
        "# TODO: clean this up\nprint('debugging')\nx = 1\n",
        encoding="utf-8",
    )
    contract = make_contract()

    result = CodeQualityVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert any("TODO" in w for w in result.warnings)
    assert any("debug statement" in w for w in result.warnings)


def test_clean_changed_file_produces_no_warnings(make_contract, git_repo):
    (git_repo / "module.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
    contract = make_contract()

    result = CodeQualityVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert result.warnings == []
