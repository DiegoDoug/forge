from fdk_verification import (
    OverallStatus,
    VerifierResult,
    VerifierStatus,
    build_report,
    render_markdown,
)


def test_build_report_passes_when_every_verifier_passes():
    results = [
        VerifierResult(name="Build", status=VerifierStatus.PASS),
        VerifierResult(name="Test", status=VerifierStatus.PASS),
        VerifierResult(name="UX", status=VerifierStatus.NOT_APPLICABLE),
    ]

    report = build_report("05", results)

    assert report.overall_status is OverallStatus.PASS
    assert report.recommendation == "CONTINUE"
    assert report.failed_results == []


def test_build_report_fails_when_any_required_verifier_fails():
    results = [
        VerifierResult(name="Build", status=VerifierStatus.PASS),
        VerifierResult(name="Test", status=VerifierStatus.FAIL, findings=["3 tests failing"]),
    ]

    report = build_report("05", results)

    assert report.overall_status is OverallStatus.FAIL
    assert report.recommendation == "REPAIR"
    assert [r.name for r in report.failed_results] == ["Test"]


def test_render_markdown_pass_report_matches_the_documented_format():
    report = build_report(
        "05",
        [
            VerifierResult(name="Specification", status=VerifierStatus.PASS),
            VerifierResult(name="Build", status=VerifierStatus.PASS),
            VerifierResult(name="UX", status=VerifierStatus.NOT_APPLICABLE),
        ],
        confidence=0.98,
    )

    rendered = render_markdown(report)

    assert "## FDK Verification Report — Phase 05" in rendered
    assert "| Specification | PASS |" in rendered
    assert "| UX | N/A |" in rendered
    assert "**Overall status:** PASS" in rendered
    assert "**Confidence:** 98%" in rendered
    assert "**Recommendation:** CONTINUE" in rendered
    assert "### Warnings" in rendered
    assert "- None" in rendered
    assert "### Failures" in rendered
    assert "### Failed verifiers" not in rendered


def test_render_markdown_fail_report_lists_failures_and_repairs():
    report = build_report(
        "05",
        [
            VerifierResult(name="Build", status=VerifierStatus.PASS),
            VerifierResult(
                name="Regression",
                status=VerifierStatus.FAIL,
                findings=["the JSON converter no longer round-trips"],
                warnings=["dark mode contrast is borderline"],
            ),
        ],
    )

    rendered = render_markdown(report)

    assert "**Overall status:** FAIL" in rendered
    assert "**Recommendation:** REPAIR" in rendered
    assert "- dark mode contrast is borderline" in rendered
    assert "### Failed verifiers" in rendered
    assert "Regression: the JSON converter no longer round-trips" in rendered
    assert "### Recommended repairs" in rendered
    assert "1. Regression: the JSON converter no longer round-trips" in rendered
