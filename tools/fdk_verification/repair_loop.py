"""The repair loop (forge-docs/15_VERIFICATION_FRAMEWORK.md §7).

A separate responsibility from Orchestrator (verify once, aggregate) and
from escalation.py (decide whether to stop-and-report) — this module only
sequences repeated verification cycles and hands remediation content to
an external repair mechanism, capped at 3 cycles per §7. It never
verifies anything itself and never edits code: "the verifier suite never
edits production code; only the Implementation Agent does" applies here
too — `on_remediation` is a notification hook, not a repair mechanism
this module implements.

Deliberately decoupled from Orchestrator: `RepairLoop.run` takes any
zero-argument callable that returns a VerificationReport, so it works
identically whether that callable wraps the real Orchestrator, the
reference Orchestrator (see reference_orchestrator.py), or a test stub —
proof that repair looping doesn't care which orchestrator implementation
produced the report it's looking at.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .report import OverallStatus, VerificationReport, render_markdown

DEFAULT_MAX_CYCLES = 3


class RepairOutcome(str, Enum):
    PASSED = "PASSED"
    RETRY_LIMIT_EXCEEDED = "RETRY_LIMIT_EXCEEDED"


@dataclass
class RepairLoopResult:
    outcome: RepairOutcome
    cycles: list[VerificationReport] = field(default_factory=list)

    @property
    def final_report(self) -> VerificationReport:
        return self.cycles[-1]

    @property
    def cycle_count(self) -> int:
        return len(self.cycles)


@dataclass
class RepairLoop:
    max_cycles: int = DEFAULT_MAX_CYCLES

    def run(
        self,
        verify: Callable[[], VerificationReport],
        *,
        on_remediation: Callable[[VerificationReport, str], None] | None = None,
    ) -> RepairLoopResult:
        """Run `verify` up to `max_cycles` times, stopping as soon as it PASSes.

        On every FAIL cycle (including the last, retry-limit-exhausting one
        — its remediation content still matters for the escalation report
        that follows), `on_remediation` is called with the failing report
        and its rendered remediation Markdown (reusing report.render_markdown
        rather than reimplementing remediation formatting).
        """
        cycles: list[VerificationReport] = []
        for _ in range(self.max_cycles):
            report = verify()
            cycles.append(report)

            if report.overall_status is OverallStatus.PASS:
                return RepairLoopResult(outcome=RepairOutcome.PASSED, cycles=cycles)

            if on_remediation is not None:
                on_remediation(report, render_markdown(report))

        return RepairLoopResult(outcome=RepairOutcome.RETRY_LIMIT_EXCEEDED, cycles=cycles)
