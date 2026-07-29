from pathlib import Path

import pytest

from fdk_verification import (
    PhaseDiscoveryError,
    VerificationContractNotFoundError,
    discover_active_phase,
    find_verification_contract,
)
from fdk_verification.phase_discovery import CONTRACT_FILENAME


def _make_phase(root, number, name, *, with_contract):
    phase_dir = root / f"Phase-{number}-{name}"
    phase_dir.mkdir(parents=True)
    (phase_dir / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    if with_contract:
        (phase_dir / CONTRACT_FILENAME).write_text("a contract\n", encoding="utf-8")
    return phase_dir


def test_discovers_the_single_phase_with_a_verification_contract(tmp_path):
    _make_phase(tmp_path, "01", "Workbench", with_contract=False)
    active_dir = _make_phase(tmp_path, "06", "Projects", with_contract=True)
    _make_phase(tmp_path, "07", "Later", with_contract=False)

    phase = discover_active_phase(tmp_path)

    assert phase.number == "06"
    assert phase.path == active_dir


def test_raises_when_no_phase_has_a_contract(tmp_path):
    _make_phase(tmp_path, "01", "Workbench", with_contract=False)
    _make_phase(tmp_path, "02", "Later", with_contract=False)

    with pytest.raises(PhaseDiscoveryError, match="no phase"):
        discover_active_phase(tmp_path)


def test_raises_when_multiple_phases_have_a_contract(tmp_path):
    _make_phase(tmp_path, "06", "Alpha", with_contract=True)
    _make_phase(tmp_path, "07", "Beta", with_contract=True)

    with pytest.raises(PhaseDiscoveryError, match="ambiguous"):
        discover_active_phase(tmp_path)


def test_raises_cleanly_on_missing_implementation_root(tmp_path):
    with pytest.raises(PhaseDiscoveryError):
        discover_active_phase(tmp_path / "does-not-exist")


def test_a_phase_without_a_readme_is_still_discovered_by_contract_presence_alone(tmp_path):
    # Discovery no longer reads README.md at all -- contract presence is
    # the entire signal. This deliberately doesn't write a README to prove
    # that.
    phase_dir = tmp_path / "Phase-06-Projects"
    phase_dir.mkdir(parents=True)
    (phase_dir / CONTRACT_FILENAME).write_text("a contract\n", encoding="utf-8")

    phase = discover_active_phase(tmp_path)

    assert phase.path == phase_dir


def test_find_verification_contract_returns_the_path_when_present(tmp_path):
    phase_dir = _make_phase(tmp_path, "06", "Projects", with_contract=True)

    phase = discover_active_phase(tmp_path)
    found = find_verification_contract(phase)

    assert found == phase_dir / CONTRACT_FILENAME


def test_find_verification_contract_fails_cleanly_if_removed_after_discovery(tmp_path):
    phase_dir = _make_phase(tmp_path, "06", "Projects", with_contract=True)
    phase = discover_active_phase(tmp_path)
    (phase_dir / CONTRACT_FILENAME).unlink()

    with pytest.raises(VerificationContractNotFoundError):
        find_verification_contract(phase)


def test_ignores_non_phase_directories(tmp_path):
    (tmp_path / "not-a-phase").mkdir()
    active_dir = _make_phase(tmp_path, "06", "Projects", with_contract=True)

    phase = discover_active_phase(tmp_path)

    assert phase.path == active_dir


def test_a_frozen_phase_folder_is_never_selected_unless_it_actually_has_a_contract(tmp_path):
    # Frozen phases are never retrofitted with a contract per
    # forge-docs/implementation/README.md §2.1 -- this proves discovery
    # relies on that policy being followed (file absence), not on parsing
    # a frozen phase's README to notice it's frozen.
    _make_phase(tmp_path, "01", "Workbench", with_contract=False)
    active_dir = _make_phase(tmp_path, "06", "Projects", with_contract=True)

    phase = discover_active_phase(tmp_path)

    assert phase.path == active_dir


def test_smoke_against_the_real_repository_fails_cleanly_or_returns_a_valid_phase():
    # As of this milestone, no real phase has adopted VERIFICATION_CONTRACT.md
    # yet, so this is expected to raise PhaseDiscoveryError -- this test
    # doesn't assert that specific outcome (it will change once a real
    # phase adopts the framework), only that discovery never crashes with
    # something other than its own typed exception.
    repo_root = Path(__file__).resolve().parents[2]
    implementation_root = repo_root / "forge-docs" / "implementation"

    try:
        phase = discover_active_phase(implementation_root)
    except PhaseDiscoveryError:
        return

    assert phase.path.is_dir()
