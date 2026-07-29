"""Verification Contract schema and parser.

Parses a phase's VERIFICATION_CONTRACT.md — authored from
forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md — into a
`VerificationContract`, per forge-docs/15_VERIFICATION_FRAMEWORK.md §5.
Independent of `report.py` and `verifier.py`: this module only knows about
contract shape, never about how a verifier runs or how a report renders.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# The 8 verifier names from forge-docs/15_VERIFICATION_FRAMEWORK.md §4,
# matching forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md §9
# exactly. This is the single source of truth every other module in this
# package validates verifier names against.
CANONICAL_VERIFIERS: frozenset[str] = frozenset(
    {
        "Specification",
        "Architecture",
        "Build",
        "Test",
        "Regression",
        "Code Quality",
        "Documentation",
        "UX",
    }
)

# Sections 1-9 of VERIFICATION_CONTRACT_TEMPLATE.md carry the contract's
# actual content; §10 (TODO) and §11 (Cross-references) are template
# scaffolding, not contract data, and are intentionally not parsed.
_REQUIRED_SECTIONS: dict[int, str] = {
    1: "Phase Metadata",
    2: "Required Tasks",
    3: "Acceptance Criteria",
    4: "Expected File Scope",
    5: "Required Validation Commands",
    6: "Architecture Constraints",
    7: "Documentation Requirements",
    8: "Regression Targets",
    9: "Required Verification Agents",
}

_SECTION_HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
_CHECKLIST_ITEM_RE = re.compile(r"^-\s*\[([ xX])\]\s*(.+?)\s*$", re.MULTILINE)
_KEY_VALUE_RE = re.compile(r"^-\s*\*\*(.+?):\*\*\s*(.*?)\s*$", re.MULTILINE)

_PLACEHOLDER_MARKERS = ("[TODO", "[Phase Name]", "[date]")


@dataclass
class ChecklistItem:
    text: str
    checked: bool


class ContractValidationError(Exception):
    """Raised so an invalid contract fails loudly instead of silently.

    Carries every issue found (not just the first), so a contract author
    or the Verification Orchestrator gets the complete list in one pass.
    """

    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("; ".join(issues))


def _normalize_verifier_name(raw: str) -> str:
    # Strips the " — required / not required" suffix the UX line in
    # VERIFICATION_CONTRACT_TEMPLATE.md §9 uses; other verifier lines have
    # no suffix to strip, so this is a no-op for them.
    return raw.split("—", 1)[0].strip()


def _split_sections(text: str) -> dict[int, str]:
    matches = list(_SECTION_HEADING_RE.finditer(text))
    sections: dict[int, str] = {}
    for i, m in enumerate(matches):
        number = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[number] = text[start:end]
    return sections


def _parse_checklist(body: str) -> list[ChecklistItem]:
    return [
        ChecklistItem(text=text, checked=mark.lower() == "x")
        for mark, text in _CHECKLIST_ITEM_RE.findall(body)
    ]


def _parse_key_values(body: str) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in _KEY_VALUE_RE.findall(body)}


@dataclass
class VerificationContract:
    phase_name: str
    phase_objective: str
    dependencies: str
    completion_definition: str
    required_tasks: list[ChecklistItem]
    acceptance_criteria: list[ChecklistItem]
    expected_scope: str
    out_of_scope: str
    required_validation_commands: list[ChecklistItem]
    architecture_constraints: list[ChecklistItem]
    documentation_requirements: list[ChecklistItem]
    regression_targets: list[ChecklistItem]
    verifier_declarations: list[ChecklistItem] = field(default_factory=list)
    source_path: Path | None = None

    @property
    def required_verifiers(self) -> frozenset[str]:
        """Verifier names whose §9 checkbox is checked, normalized.

        May contain names outside CANONICAL_VERIFIERS if the source
        document has a typo or an unrecognized entry — validate_contract
        is what catches that; this property just reports what the
        document actually declared.
        """
        return frozenset(
            _normalize_verifier_name(item.text) for item in self.verifier_declarations if item.checked
        )


def parse_contract(text: str, *, source_path: Path | None = None) -> VerificationContract:
    """Extract a VerificationContract from raw Markdown.

    Never raises on a malformed or incomplete document — a missing
    section just yields empty/default field values. Call
    `validate_contract` (or `parse_and_validate_contract`) to turn that
    into an explicit, loud failure.
    """
    sections = _split_sections(text)

    metadata = _parse_key_values(sections.get(1, ""))
    scope = _parse_key_values(sections.get(4, ""))

    return VerificationContract(
        phase_name=metadata.get("Phase name", ""),
        phase_objective=metadata.get("Phase objective", ""),
        dependencies=metadata.get("Dependencies", ""),
        completion_definition=metadata.get("Completion definition", ""),
        required_tasks=_parse_checklist(sections.get(2, "")),
        acceptance_criteria=_parse_checklist(sections.get(3, "")),
        expected_scope=scope.get("Expected new/modified files or directories", ""),
        out_of_scope=scope.get("Explicitly out of scope", ""),
        required_validation_commands=_parse_checklist(sections.get(5, "")),
        architecture_constraints=_parse_checklist(sections.get(6, "")),
        documentation_requirements=_parse_checklist(sections.get(7, "")),
        regression_targets=_parse_checklist(sections.get(8, "")),
        verifier_declarations=_parse_checklist(sections.get(9, "")),
        source_path=source_path,
    )


def _looks_unfilled(value: str) -> bool:
    return not value or any(marker in value for marker in _PLACEHOLDER_MARKERS)


def validate_contract(contract: VerificationContract, raw_text: str) -> list[str]:
    """Return every validation issue found; empty means the contract is valid.

    Per the Milestone 1 requirement: a contract missing a required section,
    or referencing a verifier that doesn't exist, must fail loudly — this
    function is what makes that failure explicit and complete rather than
    a silent gap discovered later at verifier-run time.
    """
    issues: list[str] = []

    for number, title in _REQUIRED_SECTIONS.items():
        if not re.search(rf"^##\s+{number}\.\s+", raw_text, re.MULTILINE):
            issues.append(f"missing required section: §{number} {title}")

    if _looks_unfilled(contract.phase_name):
        issues.append("§1 Phase Metadata: phase name is empty or still a template placeholder")
    if _looks_unfilled(contract.phase_objective):
        issues.append("§1 Phase Metadata: phase objective is empty or still a template placeholder")

    if not contract.required_tasks:
        issues.append("§2 Required Tasks: contract declares no tasks")
    if not contract.acceptance_criteria:
        issues.append("§3 Acceptance Criteria: contract declares no criteria")

    if not contract.verifier_declarations:
        issues.append("§9 Required Verification Agents: contract declares no verifiers")
    else:
        for item in contract.verifier_declarations:
            name = _normalize_verifier_name(item.text)
            if name not in CANONICAL_VERIFIERS:
                issues.append(
                    f"§9 Required Verification Agents: unknown verifier referenced: {name!r} "
                    f"(expected one of {sorted(CANONICAL_VERIFIERS)})"
                )
        if not contract.required_verifiers:
            issues.append("§9 Required Verification Agents: no verifier is checked as required")

    return issues


def parse_and_validate_contract(text: str, *, source_path: Path | None = None) -> VerificationContract:
    """Parse and validate in one call, raising ContractValidationError on any issue."""
    contract = parse_contract(text, source_path=source_path)
    issues = validate_contract(contract, text)
    if issues:
        raise ContractValidationError(issues)
    return contract
