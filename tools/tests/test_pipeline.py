from datetime import date

from fdk_verification import (
    PhaseDiscoveryError,
    RepairOutcome,
    parse_and_validate_contract,
    persist_reports,
    run_release_candidate_check,
    run_verification_once,
    run_verification_with_escalation,
    run_verification_with_repair,
)

from _fixtures import OK_COMMAND

CONTRACT_PASSING = f"""\
## 1. Phase Metadata

- **Phase name:** 06
- **Phase objective:** prove the pipeline works
- **Dependencies:** none
- **Completion definition:** all tasks and criteria checked

## 2. Required Tasks

- [x] T1: build the entry point

## 3. Acceptance Criteria

- [x] AC1: it works

## 4. Expected File Scope

- **Expected new/modified files or directories:** `tools/`
- **Explicitly out of scope:** `backend/`

## 5. Required Validation Commands

- [x] Build: {OK_COMMAND}

## 6. Architecture Constraints

## 7. Documentation Requirements

## 8. Regression Targets

## 9. Required Verification Agents

- [x] Specification
- [x] Build
"""

CONTRACT_ALWAYS_FAILING = """\
## 1. Phase Metadata

- **Phase name:** 06
- **Phase objective:** prove the repair/escalation path works
- **Dependencies:** none
- **Completion definition:** n/a

## 2. Required Tasks

- [x] T1: done

## 3. Acceptance Criteria

- [x] AC1: done

## 4. Expected File Scope

## 5. Required Validation Commands

## 6. Architecture Constraints

## 7. Documentation Requirements

## 8. Regression Targets

- [ ] a target nobody confirmed

## 9. Required Verification Agents

- [x] Regression
"""


def _write_phase_fixture(repo_root, contract_text, *, status="Implementation in progress"):
    phase_dir = repo_root / "forge-docs" / "implementation" / "Phase-06-Test"
    phase_dir.mkdir(parents=True)
    (phase_dir / "README.md").write_text(f"# Test\n\n> **Status:** {status}\n", encoding="utf-8")
    (phase_dir / "VERIFICATION_CONTRACT.md").write_text(contract_text, encoding="utf-8")
    return phase_dir


def test_run_verification_once_returns_a_passing_report(tmp_path):
    contract = parse_and_validate_contract(CONTRACT_PASSING)

    report = run_verification_once(contract, tmp_path)

    assert report.overall_status.value == "PASS"


def test_run_verification_with_repair_stops_after_one_cycle_on_pass(tmp_path):
    contract = parse_and_validate_contract(CONTRACT_PASSING)

    result = run_verification_with_repair(contract, tmp_path)

    assert result.outcome is RepairOutcome.PASSED
    assert result.cycle_count == 1


def test_run_verification_with_escalation_has_no_escalations_on_clean_pass(tmp_path):
    contract = parse_and_validate_contract(CONTRACT_PASSING)

    repair_result, escalations = run_verification_with_escalation(contract, tmp_path)

    assert repair_result.outcome is RepairOutcome.PASSED
    assert escalations == []


def test_persist_reports_writes_a_report_and_no_escalation_file_when_none(tmp_path):
    contract = parse_and_validate_contract(CONTRACT_PASSING)
    repair_result, escalations = run_verification_with_escalation(contract, tmp_path)
    from fdk_verification.phase_discovery import PhaseInfo

    phase = PhaseInfo(number="06", name="Test", path=tmp_path / "phase")
    history_root = tmp_path / "history"

    report_path, escalation_path = persist_reports(
        phase, repair_result, escalations, history_root, today=date(2026, 7, 29)
    )

    assert report_path.name == "2026-07-29-phase-06-verification-report.md"
    assert report_path.exists()
    assert "PASS" in report_path.read_text(encoding="utf-8")
    assert escalation_path is None
    assert not (history_root / "2026-07-29-phase-06-verification-escalation.md").exists()


def test_run_release_candidate_check_full_flow_on_a_passing_phase(tmp_path):
    phase_dir = _write_phase_fixture(tmp_path, CONTRACT_PASSING)
    readme_before = (phase_dir / "README.md").read_text(encoding="utf-8")

    outcome = run_release_candidate_check(tmp_path, today=date(2026, 7, 29))

    assert outcome.phase.number == "06"
    assert outcome.repair_result.outcome is RepairOutcome.PASSED
    assert outcome.escalations == []
    assert outcome.report_path.exists()
    assert outcome.escalation_report_path is None
    assert (phase_dir / "README.md").read_text(encoding="utf-8") == readme_before, (
        "the pipeline must never modify phase documents"
    )


def test_run_release_candidate_check_raises_cleanly_with_no_contract_anywhere(tmp_path):
    # No phase has adopted VERIFICATION_CONTRACT.md, so discovery itself
    # can't find a phase under verification -- contract presence is the
    # discovery signal, not a separate check after the fact.
    phase_dir = tmp_path / "forge-docs" / "implementation" / "Phase-06-Test"
    phase_dir.mkdir(parents=True)
    (phase_dir / "README.md").write_text("# Test\n\n> **Status:** Implementation in progress\n", encoding="utf-8")

    try:
        run_release_candidate_check(tmp_path, today=date(2026, 7, 29))
        assert False, "expected PhaseDiscoveryError"
    except PhaseDiscoveryError:
        pass

    assert not (tmp_path / "forge-docs" / "history").exists(), (
        "a failed discovery must not have side effects"
    )


def test_run_release_candidate_check_persists_both_reports_on_persistent_failure(tmp_path):
    _write_phase_fixture(tmp_path, CONTRACT_ALWAYS_FAILING)

    outcome = run_release_candidate_check(tmp_path, today=date(2026, 7, 29))

    assert outcome.repair_result.outcome is RepairOutcome.RETRY_LIMIT_EXCEEDED
    assert outcome.repair_result.cycle_count == 3
    assert outcome.escalations, "retry-limit-exceeded must escalate"
    assert outcome.report_path.exists()
    assert outcome.escalation_report_path is not None
    assert outcome.escalation_report_path.exists()
    assert "retry_limit_exceeded" in outcome.escalation_report_path.read_text(encoding="utf-8")
