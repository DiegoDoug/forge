"""Phase discovery (4A step 1 — forge-docs/15_VERIFICATION_FRAMEWORK.md §1).

Discovers the FDK phase currently undergoing Release Candidate
verification, without a human pointing to it explicitly. This module only
reads implementation/Phase-NN-*/ — it never writes anything, so it cannot
change phase state.

The discovery signal is the presence of VERIFICATION_CONTRACT.md itself,
not a phase's free-text README `Status:` line. An earlier version of this
module parsed that prose (looking for "frozen" / "template scaffold"), but
against this repo's real state that produced a genuine ambiguity: two
phases were simultaneously "not frozen, not a placeholder" for unrelated
reasons (one mid-lifecycle, one already past sign-off but not yet tagged),
and prose parsing had no principled way to prefer one. The framework
doesn't need to know which phase is "active" in a general, human sense —
only which phase is under verification, and per
forge-docs/implementation/README.md §2.1, that is precisely the set of
phases that have adopted VERIFICATION_CONTRACT.md (created before
implementation begins, from Phase 05 onward, never retrofitted onto a
frozen phase). File presence is deterministic, structural metadata; a
status paragraph is not — so that's the whole signal this module needs.

The same "fail loudly" discipline still applies at this narrower scope:
zero phases with a contract (true today — no phase has adopted the
framework yet) or more than one (a real overlap, e.g. two phases in
parallel development) both raise PhaseDiscoveryError rather than guessing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_PHASE_DIR_RE = re.compile(r"^Phase-(\d+)-(.+)$")

CONTRACT_FILENAME = "VERIFICATION_CONTRACT.md"


class PhaseDiscoveryError(Exception):
    """Raised when the phase under verification can't be determined unambiguously."""


class VerificationContractNotFoundError(Exception):
    """Raised when a phase expected to have VERIFICATION_CONTRACT.md doesn't."""


@dataclass(frozen=True)
class PhaseInfo:
    number: str
    name: str
    path: Path


def _iter_phase_dirs(implementation_root: Path) -> list[Path]:
    if not implementation_root.is_dir():
        raise PhaseDiscoveryError(f"implementation root does not exist: {implementation_root}")
    dirs = [p for p in implementation_root.iterdir() if p.is_dir() and _PHASE_DIR_RE.match(p.name)]
    return sorted(dirs, key=lambda p: _PHASE_DIR_RE.match(p.name).group(1))


def discover_active_phase(implementation_root: Path) -> PhaseInfo:
    """Find the single phase directory that contains VERIFICATION_CONTRACT.md.

    Raises PhaseDiscoveryError if zero or more than one phase qualifies —
    ambiguity is a failure, not something this function resolves by guessing.
    """
    candidates: list[PhaseInfo] = []

    for phase_dir in _iter_phase_dirs(implementation_root):
        if (phase_dir / CONTRACT_FILENAME).is_file():
            match = _PHASE_DIR_RE.match(phase_dir.name)
            candidates.append(PhaseInfo(number=match.group(1), name=match.group(2), path=phase_dir))

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise PhaseDiscoveryError(
            f"no phase under {implementation_root} has a {CONTRACT_FILENAME} — "
            "the framework isn't adopted by any phase yet"
        )
    raise PhaseDiscoveryError(
        f"ambiguous phase under verification — {len(candidates)} phases have a "
        f"{CONTRACT_FILENAME}: {[c.path.name for c in candidates]}"
    )


def find_verification_contract(phase: PhaseInfo) -> Path:
    """Locate the phase's VERIFICATION_CONTRACT.md, failing cleanly if it's gone.

    Discovery already requires this file to exist to select the phase at
    all, so this should never actually fail in practice — kept as a
    defensive, explicit check against a file removed between calls rather
    than an implicit assumption.
    """
    contract_path = phase.path / CONTRACT_FILENAME
    if not contract_path.is_file():
        raise VerificationContractNotFoundError(
            f"phase {phase.path.name} has no {CONTRACT_FILENAME} at {contract_path}"
        )
    return contract_path
