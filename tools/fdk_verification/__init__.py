"""FDK Verification Framework infrastructure (Milestones 1-3).

Implements the Verification Contract schema/parser, the report model, the
Verifier interface and its 8 concrete verifiers, the Orchestrator, the
repair loop, the escalation policy, and the reference Orchestrator
specified in forge-docs/15_VERIFICATION_FRAMEWORK.md and built per
forge-docs/templates/prompts/VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md.

Milestone 1-3 scope only: nothing in this package hooks into an FDK
phase's lifecycle or auto-continues anything. See
forge-docs/15_VERIFICATION_FRAMEWORK.md §10 for what's built vs. what's
next, and tools/fdk_verification/README.md for the per-milestone detail.
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
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "DEFAULT_MAX_CYCLES",
    "ChecklistItem",
    "ContractValidationError",
    "Escalation",
    "EscalationCondition",
    "MissingVerifierError",
    "OverallStatus",
    "Orchestrator",
    "ReferenceOrchestrator",
    "RepairLoop",
    "RepairLoopResult",
    "RepairOutcome",
    "UnregisteredVerifierError",
    "VerificationContract",
    "VerificationReport",
    "Verifier",
    "VerifierResult",
    "VerifierStatus",
    "build_report",
    "evaluate",
    "parse_and_validate_contract",
    "parse_contract",
    "render_escalation_report",
    "render_markdown",
    "validate_contract",
    "verifiers",
]
