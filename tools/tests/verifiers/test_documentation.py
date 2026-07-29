from fdk_verification import VerifierStatus
from fdk_verification.verifiers import DocumentationVerifier


def test_not_applicable_when_nothing_required(make_contract, git_repo):
    contract = make_contract(documentation_requirements=[])

    result = DocumentationVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.NOT_APPLICABLE


def test_passes_when_the_required_doc_was_actually_changed(make_contract, checklist, git_repo):
    (git_repo / "CURRENT_STATE.md").write_text("state\n", encoding="utf-8")
    contract = make_contract(
        documentation_requirements=checklist(("Update `CURRENT_STATE.md`", True))
    )

    result = DocumentationVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS


def test_fails_when_the_required_doc_was_not_changed(make_contract, checklist, git_repo):
    contract = make_contract(
        documentation_requirements=checklist(("Update `CURRENT_STATE.md`", True))
    )

    result = DocumentationVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.FAIL
    assert any("CURRENT_STATE.md" in f for f in result.findings)


def test_warns_instead_of_guessing_on_unparseable_requirements(make_contract, checklist, git_repo):
    contract = make_contract(
        documentation_requirements=checklist(("Update the relevant docs somewhere", True))
    )

    result = DocumentationVerifier().run(contract, git_repo)

    assert result.status is VerifierStatus.PASS
    assert result.findings == []
    assert any("no parseable file path" in w for w in result.warnings)
