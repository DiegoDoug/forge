"""Escalation policy (forge-docs/15_VERIFICATION_FRAMEWORK.md §8).

A separate responsibility from Orchestrator (verify once, aggregate) and
repair_loop.py (retry bookkeeping) — this module only decides whether a
stop-and-report condition has been hit. It never runs a verifier, a
repair, or another verification cycle.

Of the 6 escalation conditions in §8, `evaluate()` auto-detects 2
mechanically from a RepairLoopResult, plus a 3rd on a best-effort basis:

- RETRY_LIMIT_EXCEEDED — the repair loop ran out of cycles.
- CONFIDENCE_BELOW_THRESHOLD — the final report's confidence, if set,
  fell below `confidence_threshold`.
- ARCHITECTURE_SPEC_CONFLICT (heuristic, not proof) — the same
  Architecture-verifier finding recurred, unchanged, across every cycle
  of a retry-limit-exceeded run — a signal that repair attempts aren't
  actually resolving it, not a certainty that it's a real conflict.

The remaining 3 require judgment this generic library structurally can't
make from a VerificationReport alone — §8 maps each to an existing "must
ask first" trigger a human or a Claude Code session applies, not
something derivable from verifier output:

- AMBIGUOUS_REQUIREMENTS
- DESTRUCTIVE_OPERATION_REQUIRED
- BLOCKED_EXTERNAL_DEPENDENCY

An external caller raises these directly — `Escalation(condition, detail)`
— when it determines the situation applies; `evaluate()` never emits them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .report import VerificationReport, render_markdown
from .repair_loop import RepairLoopResult, RepairOutcome

DEFAULT_CONFIDENCE_THRESHOLD = 0.7


class EscalationCondition(str, Enum):
    ARCHITECTURE_SPEC_CONFLICT = "architecture_spec_conflict"
    AMBIGUOUS_REQUIREMENTS = "ambiguous_requirements"
    DESTRUCTIVE_OPERATION_REQUIRED = "destructive_operation_required"
    BLOCKED_EXTERNAL_DEPENDENCY = "blocked_external_dependency"
    RETRY_LIMIT_EXCEEDED = "retry_limit_exceeded"
    CONFIDENCE_BELOW_THRESHOLD = "confidence_below_threshold"


@dataclass
class Escalation:
    condition: EscalationCondition
    detail: str


def _recurring_architecture_failure(cycles: list[VerificationReport]) -> Escalation | None:
    if len(cycles) < 2:
        return None

    def architecture_findings(report: VerificationReport) -> frozenset[str] | None:
        for result in report.results:
            if result.name == "Architecture":
                return frozenset(result.findings) if result.findings else None
        return None

    first = architecture_findings(cycles[0])
    if not first:
        return None
    if all(architecture_findings(report) == first for report in cycles[1:]):
        return Escalation(
            condition=EscalationCondition.ARCHITECTURE_SPEC_CONFLICT,
            detail=(
                "the same Architecture finding recurred unchanged across every repair cycle: "
                + "; ".join(sorted(first))
            ),
        )
    return None


def evaluate(
    repair_result: RepairLoopResult,
    *,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> list[Escalation]:
    escalations: list[Escalation] = []

    if repair_result.outcome is RepairOutcome.RETRY_LIMIT_EXCEEDED:
        escalations.append(
            Escalation(
                condition=EscalationCondition.RETRY_LIMIT_EXCEEDED,
                detail=f"{repair_result.cycle_count} repair cycles ran with no PASS",
            )
        )
        recurring = _recurring_architecture_failure(repair_result.cycles)
        if recurring is not None:
            escalations.append(recurring)

    confidence = repair_result.final_report.confidence
    if confidence is not None and confidence < confidence_threshold:
        escalations.append(
            Escalation(
                condition=EscalationCondition.CONFIDENCE_BELOW_THRESHOLD,
                detail=f"confidence {confidence:.0%} is below the {confidence_threshold:.0%} threshold",
            )
        )

    return escalations


def render_escalation_report(escalations: list[Escalation], repair_result: RepairLoopResult) -> str:
    lines = ["## FDK Verification Escalation", ""]
    lines.append(f"**Cycles run:** {repair_result.cycle_count}")
    lines.append(f"**Final status:** {repair_result.final_report.overall_status.value}")
    lines.append("")
    lines.append("### Escalation conditions")
    if escalations:
        lines += [f"- **{esc.condition.value}**: {esc.detail}" for esc in escalations]
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Latest verification report")
    lines.append(render_markdown(repair_result.final_report))
    return "\n".join(lines)
