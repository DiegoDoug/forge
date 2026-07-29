from fdk_verification import (
    Escalation,
    EscalationCondition,
    RepairLoopResult,
    RepairOutcome,
    evaluate,
    render_escalation_report,
)

from _fixtures import failing_report, passing_report


def test_no_escalation_on_a_clean_pass():
    result = RepairLoopResult(outcome=RepairOutcome.PASSED, cycles=[passing_report(confidence=0.95)])

    assert evaluate(result) == []


def test_retry_limit_exceeded_is_detected():
    result = RepairLoopResult(
        outcome=RepairOutcome.RETRY_LIMIT_EXCEEDED,
        cycles=[failing_report(finding="a", verifier_name="Build") for _ in range(3)],
    )

    escalations = evaluate(result)

    assert any(e.condition is EscalationCondition.RETRY_LIMIT_EXCEEDED for e in escalations)


def test_confidence_below_threshold_is_detected_even_on_pass():
    result = RepairLoopResult(outcome=RepairOutcome.PASSED, cycles=[passing_report(confidence=0.4)])

    escalations = evaluate(result, confidence_threshold=0.7)

    assert [e.condition for e in escalations] == [EscalationCondition.CONFIDENCE_BELOW_THRESHOLD]


def test_confidence_at_or_above_threshold_does_not_escalate():
    result = RepairLoopResult(outcome=RepairOutcome.PASSED, cycles=[passing_report(confidence=0.9)])

    assert evaluate(result, confidence_threshold=0.7) == []


def test_missing_confidence_is_not_treated_as_below_threshold():
    result = RepairLoopResult(outcome=RepairOutcome.PASSED, cycles=[passing_report(confidence=None)])

    assert evaluate(result) == []


def test_recurring_identical_architecture_failure_flags_a_conflict_heuristically():
    same_finding = "dependency direction violated in the same spot every time"
    cycles = [
        failing_report(finding=same_finding, verifier_name="Architecture") for _ in range(3)
    ]
    result = RepairLoopResult(outcome=RepairOutcome.RETRY_LIMIT_EXCEEDED, cycles=cycles)

    escalations = evaluate(result)

    assert any(e.condition is EscalationCondition.ARCHITECTURE_SPEC_CONFLICT for e in escalations)


def test_changing_architecture_failures_do_not_trigger_the_conflict_heuristic():
    cycles = [
        failing_report(finding="finding A", verifier_name="Architecture"),
        failing_report(finding="finding B", verifier_name="Architecture"),
        failing_report(finding="finding C", verifier_name="Architecture"),
    ]
    result = RepairLoopResult(outcome=RepairOutcome.RETRY_LIMIT_EXCEEDED, cycles=cycles)

    escalations = evaluate(result)

    assert not any(e.condition is EscalationCondition.ARCHITECTURE_SPEC_CONFLICT for e in escalations)


def test_the_three_judgment_call_conditions_are_never_auto_emitted():
    result = RepairLoopResult(
        outcome=RepairOutcome.RETRY_LIMIT_EXCEEDED,
        cycles=[failing_report() for _ in range(3)],
    )

    escalations = evaluate(result)
    conditions = {e.condition for e in escalations}

    assert EscalationCondition.AMBIGUOUS_REQUIREMENTS not in conditions
    assert EscalationCondition.DESTRUCTIVE_OPERATION_REQUIRED not in conditions
    assert EscalationCondition.BLOCKED_EXTERNAL_DEPENDENCY not in conditions


def test_judgment_call_conditions_can_still_be_constructed_and_raised_externally():
    escalation = Escalation(
        condition=EscalationCondition.AMBIGUOUS_REQUIREMENTS,
        detail="the spec doesn't define what 'complete' means for T4",
    )

    assert escalation.condition is EscalationCondition.AMBIGUOUS_REQUIREMENTS


def test_render_escalation_report_includes_conditions_and_the_final_report():
    result = RepairLoopResult(
        outcome=RepairOutcome.RETRY_LIMIT_EXCEEDED,
        cycles=[failing_report(finding="still broken") for _ in range(3)],
    )
    escalations = evaluate(result)

    rendered = render_escalation_report(escalations, result)

    assert "## FDK Verification Escalation" in rendered
    assert "retry_limit_exceeded" in rendered
    assert "### Latest verification report" in rendered
    assert "still broken" in rendered
