"""FDK Verification Framework infrastructure (Milestones 1-3, 4A).

Implements the Verification Contract schema/parser, the report model, the
Verifier interface and its 8 concrete verifiers, the Orchestrator, the
repair loop, the escalation policy, the reference Orchestrator, phase
discovery, and the Release Candidate pipeline specified in
forge-docs/15_VERIFICATION_FRAMEWORK.md and built per
forge-docs/templates/prompts/VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md.

Milestone 4A scope: the pipeline runs automatically at the Release
Candidate stage and persists its results. There is no capability anywhere
in this package to advance a phase — that is Milestone 4B, gated on a real
dry run. See forge-docs/15_VERIFICATION_FRAMEWORK.md §10 for what's built
vs. what's next, and tools/fdk_verification/README.md for per-milestone
detail.
"""

from . import verifiers
from .contract import (
    ChecklistItem,
    ContractValidationError,
    VerificationContract,
    parse_and_validate_contract,
    parse_contract,
    validate_contract,
)
from .escalation import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    Escalation,
    EscalationCondition,
    evaluate,
    render_escalation_report,
)
from .orchestrator import Orchestrator, UnregisteredVerifierError
from .phase_discovery import (
    CONTRACT_FILENAME,
    PhaseDiscoveryError,
    PhaseInfo,
    VerificationContractNotFoundError,
    discover_active_phase,
    find_verification_contract,
)
from .pipeline import (
    RCVerificationOutcome,
    persist_reports,
    run_release_candidate_check,
    run_verification_once,
    run_verification_with_escalation,
    run_verification_with_repair,
)
from .reference_orchestrator import MissingVerifierError, ReferenceOrchestrator
from .repair_loop import DEFAULT_MAX_CYCLES, RepairLoop, RepairLoopResult, RepairOutcome
from .report import (
    OverallStatus,
    VerificationReport,
    VerifierResult,
    VerifierStatus,
    build_report,
    render_markdown,
)
from .verifier import CANONICAL_VERIFIERS, Verifier

__all__ = [
    "CANONICAL_VERIFIERS",
    "CONTRACT_FILENAME",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "DEFAULT_MAX_CYCLES",
    "ChecklistItem",
    "ContractValidationError",
    "Escalation",
    "EscalationCondition",
    "MissingVerifierError",
    "OverallStatus",
    "Orchestrator",
    "PhaseDiscoveryError",
    "PhaseInfo",
    "RCVerificationOutcome",
    "ReferenceOrchestrator",
    "RepairLoop",
    "RepairLoopResult",
    "RepairOutcome",
    "UnregisteredVerifierError",
    "VerificationContract",
    "VerificationContractNotFoundError",
    "VerificationReport",
    "Verifier",
    "VerifierResult",
    "VerifierStatus",
    "build_report",
    "discover_active_phase",
    "evaluate",
    "find_verification_contract",
    "parse_and_validate_contract",
    "parse_contract",
    "persist_reports",
    "render_escalation_report",
    "render_markdown",
    "run_release_candidate_check",
    "run_verification_once",
    "run_verification_with_escalation",
    "run_verification_with_repair",
    "validate_contract",
    "verifiers",
]
