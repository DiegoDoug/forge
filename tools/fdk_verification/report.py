"""The Report model (forge-docs/15_VERIFICATION_FRAMEWORK.md §6).

Deliberately independent of `contract.py` and `verifier.py` — a report can
be built from any set of `VerifierResult`s, hand-constructed or real, which
is what lets this module's Markdown format be proven before any real
verifier exists (Milestone 1's stated requirement).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VerifierStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "N/A"


class OverallStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class VerifierResult:
    name: str
    status: VerifierStatus
    findings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class VerificationReport:
    phase_name: str
    results: list[VerifierResult]
    overall_status: OverallStatus
    confidence: float | None = None
    recommendation: str = ""

    @property
    def failed_results(self) -> list[VerifierResult]:
        return [r for r in self.results if r.status is VerifierStatus.FAIL]

    @property
    def warnings(self) -> list[str]:
        return [w for r in self.results for w in r.warnings]


def build_report(
    phase_name: str,
    results: list[VerifierResult],
    *,
    confidence: float | None = None,
) -> VerificationReport:
    """Aggregate verifier results into a single PASS/FAIL decision.

    Per forge-docs/15_VERIFICATION_FRAMEWORK.md §3: FAIL if any required
    verifier fails; PASS only if every required verifier passes. A
    verifier reporting NOT_APPLICABLE (declared but structurally
    unrunnable, e.g. UX criteria a headless session can't check per
    forge-docs/12_BUG_CLASSIFICATION.md §4) does not by itself fail the
    run — only an explicit FAIL does.
    """
    overall = (
        OverallStatus.FAIL
        if any(r.status is VerifierStatus.FAIL for r in results)
        else OverallStatus.PASS
    )
    recommendation = "CONTINUE" if overall is OverallStatus.PASS else "REPAIR"
    return VerificationReport(
        phase_name=phase_name,
        results=results,
        overall_status=overall,
        confidence=confidence,
        recommendation=recommendation,
    )


def render_markdown(report: VerificationReport) -> str:
    """Render a report in the plain-Markdown format from §6 (not ASCII boxes)."""
    lines = [f"## FDK Verification Report — Phase {report.phase_name}", ""]
    lines += ["| Verifier | Result |", "|---|---|"]
    for result in report.results:
        lines.append(f"| {result.name} | {result.status.value} |")
    lines.append("")
    lines.append(f"**Overall status:** {report.overall_status.value}")
    if report.confidence is not None:
        lines.append(f"**Confidence:** {report.confidence:.0%}")
    lines.append(f"**Recommendation:** {report.recommendation}")
    lines.append("")

    lines.append("### Warnings")
    warnings = report.warnings
    lines += [f"- {w}" for w in warnings] if warnings else ["- None"]
    lines.append("")

    failed = report.failed_results
    if not failed:
        lines.append("### Failures")
        lines.append("- None")
        return "\n".join(lines)

    lines.append("### Failed verifiers")
    for result in failed:
        detail = "; ".join(result.findings) if result.findings else "no findings recorded"
        lines.append(f"- {result.name}: {detail}")
    lines.append("")

    lines.append("### Recommended repairs")
    repair_items = [
        f"{result.name}: {finding}" for result in failed for finding in result.findings
    ]
    if repair_items:
        lines += [f"{i}. {item}" for i, item in enumerate(repair_items, start=1)]
    else:
        lines.append("1. See failed verifiers above — no specific findings recorded.")

    return "\n".join(lines)
