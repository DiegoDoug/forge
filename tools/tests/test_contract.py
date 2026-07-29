from pathlib import Path

import pytest

from fdk_verification import (
    ContractValidationError,
    parse_and_validate_contract,
    parse_contract,
    validate_contract,
)

TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "forge-docs"
    / "implementation"
    / "VERIFICATION_CONTRACT_TEMPLATE.md"
)

FILLED_CONTRACT = """\
# Test Phase — Verification Contract

---

## 1. Phase Metadata

- **Phase name:** Test Phase
- **Phase objective:** Prove the parser works.
- **Dependencies:** None.
- **Completion definition:** All tasks and criteria below are met.

## 2. Required Tasks

- [x] T1: Do the thing.
- [ ] T2: Do the other thing.

## 3. Acceptance Criteria

- [x] AC1: The thing works.

## 4. Expected File Scope

- **Expected new/modified files or directories:** `tools/fdk_verification/`
- **Explicitly out of scope:** `backend/app/`

## 5. Required Validation Commands

- [x] Test: pytest tools/tests

## 6. Architecture Constraints

- [x] No cross-feature imports.

## 7. Documentation Requirements

- [x] Update CURRENT_STATE.md.

## 8. Regression Targets

- [x] Existing converters still work.

## 9. Required Verification Agents

- [x] Specification
- [ ] Architecture
- [x] Build
- [x] Test
- [ ] Regression
- [ ] Code Quality
- [ ] Documentation
- [ ] UX — not required

## 10. TODO

- [ ] none

## 11. Cross-references

- [README.md](README.md)
"""


def test_parse_contract_extracts_metadata_and_checklists():
    contract = parse_contract(FILLED_CONTRACT)

    assert contract.phase_name == "Test Phase"
    assert contract.phase_objective == "Prove the parser works."
    assert [item.text for item in contract.required_tasks] == [
        "T1: Do the thing.",
        "T2: Do the other thing.",
    ]
    assert [item.checked for item in contract.required_tasks] == [True, False]
    assert contract.expected_scope == "`tools/fdk_verification/`"
    assert contract.out_of_scope == "`backend/app/`"


def test_required_verifiers_reflects_only_checked_items():
    contract = parse_contract(FILLED_CONTRACT)

    assert contract.required_verifiers == frozenset({"Specification", "Build", "Test"})


def test_filled_contract_passes_validation():
    issues = validate_contract(parse_contract(FILLED_CONTRACT), FILLED_CONTRACT)

    assert issues == []


def test_unfilled_template_fails_validation_loudly():
    raw = TEMPLATE_PATH.read_text(encoding="utf-8")
    contract = parse_contract(raw)

    issues = validate_contract(contract, raw)

    assert issues, "an unfilled template must never validate as a real contract"
    assert any("phase name" in issue for issue in issues)
    assert any("no verifier is checked as required" in issue for issue in issues)
    assert not any("missing required section" in issue for issue in issues), (
        "the template itself defines every required section — this failing would mean "
        "VERIFICATION_CONTRACT_TEMPLATE.md and the parser have drifted apart"
    )


def test_unknown_verifier_reference_fails_loudly():
    text = FILLED_CONTRACT.replace("- [x] Specification", "- [x] Security")

    issues = validate_contract(parse_contract(text), text)

    assert any("unknown verifier referenced: 'Security'" in issue for issue in issues)


def test_missing_section_fails_loudly():
    text = FILLED_CONTRACT.replace("## 6. Architecture Constraints", "## Renamed Section")

    issues = validate_contract(parse_contract(text), text)

    assert any("missing required section: §6" in issue for issue in issues)


def test_parse_and_validate_contract_raises_with_all_issues():
    with pytest.raises(ContractValidationError) as excinfo:
        parse_and_validate_contract(TEMPLATE_PATH.read_text(encoding="utf-8"))

    assert len(excinfo.value.issues) > 1
