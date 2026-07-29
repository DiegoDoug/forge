"""The Release Candidate verification pipeline (4A steps 2-6).

Built as a vertical slice, each function composing the previous one, per
forge-docs/templates/prompts/VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md's
Milestone 4A order:

  run_verification_once          (step 2 — verify, once)
  run_verification_with_repair   (step 3 — + RepairLoop, capped at 3 cycles)
  run_verification_with_escalation (step 4 — + escalation policy)
  persist_reports                (step 5 — write to forge-docs/history/)
  run_release_candidate_check    (step 6 — the FDK lifecycle entry point)

None of these functions can advance a phase. There is no function anywhere
in this module — or this package — named or shaped like one. That is a
Milestone 4B concern; see forge-docs/15_VERIFICATION_FRAMEWORK.md §10 and
the kickoff prompt's Milestone 4B precondition. If you are reading this
file wondering where to add one: don't — that is the signal to stop and
open the 4B effort instead, per this milestone's explicit instruction not
to add so much as a disabled or unused advance-to-next-phase function.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Mapping

from .contract import VerificationContract, parse_and_validate_contract
from .escalation import DEFAULT_CONFIDENCE_THRESHOLD, Escalation, evaluate, render_escalation_report
from .orchestrator import Orchestrator
from .phase_discovery import PhaseInfo, discover_active_phase, find_verification_contract
from .repair_loop import RepairLoop, RepairLoopResult
from .report import VerificationReport, render_markdown
from .verifier import Verifier
from .verifiers import default_registry


def run_verification_once(
    contract: VerificationContract,
    workspace_root: Path,
    verifiers: Mapping[str, Verifier] | None = None,
) -> VerificationReport:
    """Step 2: load a contract, build the verifier registry, run the Orchestrator once."""
    registry = verifiers if verifiers is not None else default_registry()
    return Orchestrator(registry).run(contract, workspace_root)


def run_verification_with_repair(
    contract: VerificationContract,
    workspace_root: Path,
    verifiers: Mapping[str, Verifier] | None = None,
    *,
    max_cycles: int = 3,
) -> RepairLoopResult:
    """Step 3: wrap step 2 with RepairLoop, capped at max_cycles.

    Still makes no lifecycle decision — this returns the repair outcome and
    nothing else acts on it yet.
    """

    def verify() -> VerificationReport:
        return run_verification_once(contract, workspace_root, verifiers)

    return RepairLoop(max_cycles=max_cycles).run(verify)


def run_verification_with_escalation(
    contract: VerificationContract,
    workspace_root: Path,
    verifiers: Mapping[str, Verifier] | None = None,
    *,
    max_cycles: int = 3,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> tuple[RepairLoopResult, list[Escalation]]:
    """Step 4: layer the escalation policy on top of step 3's repair result.

    Still stops here — this produces the escalation output; nothing yet
    acts on it beyond returning it for step 5 to persist.
    """
    repair_result = run_verification_with_repair(contract, workspace_root, verifiers, max_cycles=max_cycles)
    escalations = evaluate(repair_result, confidence_threshold=confidence_threshold)
    return repair_result, escalations


def _report_document(phase: PhaseInfo, repair_result: RepairLoopResult, today: date) -> str:
    lines = [
        f"# FDK Verification Report — Phase {phase.number} — {today.isoformat()}",
        "",
        f"> **Phase:** [Phase-{phase.number}-{phase.name}](../implementation/{phase.path.name}/README.md)",
        f"> **Contract:** [{phase.path.name}/VERIFICATION_CONTRACT.md](../implementation/{phase.path.name}/VERIFICATION_CONTRACT.md)",
        f"> **Cycles run:** {repair_result.cycle_count}",
        f"> **Generated:** {today.isoformat()}",
        "",
        "---",
        "",
        render_markdown(repair_result.final_report),
    ]
    return "\n".join(lines)


def _escalation_document(
    phase: PhaseInfo, repair_result: RepairLoopResult, escalations: list[Escalation], today: date
) -> str:
    lines = [
        f"# FDK Verification Escalation — Phase {phase.number} — {today.isoformat()}",
        "",
        f"> **Phase:** [Phase-{phase.number}-{phase.name}](../implementation/{phase.path.name}/README.md)",
        f"> **Generated:** {today.isoformat()}",
        "",
        "---",
        "",
        render_escalation_report(escalations, repair_result),
    ]
    return "\n".join(lines)


def persist_reports(
    phase: PhaseInfo,
    repair_result: RepairLoopResult,
    escalations: list[Escalation],
    history_root: Path,
    *,
    today: date | None = None,
) -> tuple[Path, Path | None]:
    """Step 5: write the verification report, and the escalation report if applicable,
    following this repo's history/ naming convention (see
    forge-docs/history/CHECKPOINT_LOG_TEMPLATE.md for the established pattern).
    """
    today = today or date.today()
    history_root.mkdir(parents=True, exist_ok=True)

    report_path = history_root / f"{today.isoformat()}-phase-{phase.number}-verification-report.md"
    report_path.write_text(_report_document(phase, repair_result, today), encoding="utf-8")

    escalation_path: Path | None = None
    if escalations:
        escalation_path = history_root / f"{today.isoformat()}-phase-{phase.number}-verification-escalation.md"
        escalation_path.write_text(_escalation_document(phase, repair_result, escalations, today), encoding="utf-8")

    return report_path, escalation_path


@dataclass
class RCVerificationOutcome:
    phase: PhaseInfo
    contract: VerificationContract
    repair_result: RepairLoopResult
    escalations: list[Escalation]
    report_path: Path
    escalation_report_path: Path | None


def run_release_candidate_check(
    repo_root: Path,
    *,
    verifiers: Mapping[str, Verifier] | None = None,
    max_cycles: int = 3,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    today: date | None = None,
) -> RCVerificationOutcome:
    """Step 6: the single entry point the FDK Release Candidate stage invokes.

    Discovers the active phase and its contract, runs verify -> repair ->
    escalate, and persists the results — replacing the manual audit only as
    the audit *mechanism*. This function does not, and structurally cannot,
    change phase state: it only reads implementation/ and writes new,
    additively-named files under history/. It returns a report of what
    happened; it never acts on that report beyond writing it down.
    """
    implementation_root = repo_root / "forge-docs" / "implementation"
    history_root = repo_root / "forge-docs" / "history"

    phase = discover_active_phase(implementation_root)
    contract_path = find_verification_contract(phase)
    contract = parse_and_validate_contract(contract_path.read_text(encoding="utf-8"), source_path=contract_path)

    repair_result, escalations = run_verification_with_escalation(
        contract, repo_root, verifiers, max_cycles=max_cycles, confidence_threshold=confidence_threshold
    )
    report_path, escalation_path = persist_reports(phase, repair_result, escalations, history_root, today=today)

    return RCVerificationOutcome(
        phase=phase,
        contract=contract,
        repair_result=repair_result,
        escalations=escalations,
        report_path=report_path,
        escalation_report_path=escalation_path,
    )
