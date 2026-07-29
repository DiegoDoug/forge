"""Deterministic replay tests for RepairLoop.

Each test scripts a fixed sequence of canned VerificationReports (a
"replay") rather than depending on real verifiers, subprocess timing, or
any I/O — the point is to pin down RepairLoop's control flow (cycle
count, when on_remediation fires, when the retry limit kicks in)
independent of anything a real verify() call could vary.
"""

from fdk_verification import RepairLoop, RepairOutcome

from _fixtures import failing_report, passing_report


def _replay(*reports):
    iterator = iter(reports)
    return lambda: next(iterator)


def test_pass_on_the_first_cycle_runs_exactly_once():
    verify = _replay(passing_report())

    result = RepairLoop().run(verify)

    assert result.outcome is RepairOutcome.PASSED
    assert result.cycle_count == 1


def test_fail_fail_pass_replays_deterministically_and_stops_at_pass():
    verify = _replay(failing_report(), failing_report(), passing_report())
    remediations = []

    result = RepairLoop(max_cycles=3).run(
        verify, on_remediation=lambda report, markdown: remediations.append((report, markdown))
    )

    assert result.outcome is RepairOutcome.PASSED
    assert result.cycle_count == 3
    assert len(remediations) == 2, "on_remediation must fire for both FAIL cycles, not the final PASS"
    assert all("### Recommended repairs" in markdown for _, markdown in remediations)


def test_persistent_failure_hits_the_retry_limit_after_exactly_three_cycles():
    verify = _replay(failing_report(), failing_report(), failing_report())
    remediations = []

    result = RepairLoop(max_cycles=3).run(verify, on_remediation=lambda report, markdown: remediations.append(report))

    assert result.outcome is RepairOutcome.RETRY_LIMIT_EXCEEDED
    assert result.cycle_count == 3
    assert len(remediations) == 3, "the final failing cycle's remediation still matters for the escalation report"


def test_default_max_cycles_is_three_per_the_framework_spec():
    assert RepairLoop().max_cycles == 3


def test_runs_without_a_remediation_hook_at_all():
    verify = _replay(passing_report())

    result = RepairLoop().run(verify)

    assert result.outcome is RepairOutcome.PASSED


def test_never_calls_verify_more_than_max_cycles_times():
    calls = []

    def verify():
        calls.append(1)
        return failing_report()

    RepairLoop(max_cycles=3).run(verify)

    assert len(calls) == 3
