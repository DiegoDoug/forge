"""Contract-driven command extraction, shared by Build and Test.

Neither verifier hardcodes a specific tool (tsc/eslint/pytest/...) by
name — both only know how to run whatever the contract's §5 declares,
per the Orchestrator-replaceable principle applied one level down to the
verifiers themselves.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..contract import ChecklistItem
from ._shell import run_command

_LABELED_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 /_-]*?):\s*(.+)$")

# Shared between Build and Test so neither verifier module has to import
# the other to agree on which §5 labels are whose domain — that would be
# an inter-verifier dependency, which both must avoid.
BUILD_LABEL_KEYWORDS = ("lint", "typecheck", "type check", "build", "docker", "full-stack", "full stack")


def labeled_commands(items: list[ChecklistItem]) -> list[tuple[str, str]]:
    """Extract (label, command) pairs from checked items shaped 'Label: command'.

    A checked item that isn't in that shape is skipped, not errored — a
    contract author who wrote free text instead of a runnable command
    simply won't have that item executed.
    """
    pairs = []
    for item in items:
        if not item.checked:
            continue
        match = _LABELED_RE.match(item.text)
        if match:
            pairs.append((match.group(1).strip(), match.group(2).strip()))
    return pairs


def run_labeled_commands(commands: list[tuple[str, str]], workspace_root: Path) -> list[str]:
    """Run each (label, command) pair; return one finding per non-zero exit."""
    findings = []
    for label, command in commands:
        result = run_command(command, workspace_root)
        if result.returncode != 0:
            findings.append(f"{label} ({command!r}) exited {result.returncode}: {result.output[-500:]}")
    return findings
