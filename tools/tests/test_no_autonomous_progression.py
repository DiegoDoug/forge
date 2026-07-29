"""4A step 7: the regression guard.

These tests are the durable trip-wire this milestone's own instructions
require, not a one-time confirmation: proof, not just a design claim, that
no advance-to-next-phase capability exists anywhere in this package, that
a full pipeline run never mutates a phase document (including on a clean
PASS), and that no git command capable of mutating repository or remote
state is ever constructed by this package's source.

Per the instruction that prompted this file: reaching the point where a
test here starts failing is the signal to stop and open the Milestone 4B
effort, not to patch around it. This file must still pass, unmodified,
after 4B lands (4B adds an activation function; it does not touch this
package's existing pipeline, and it does not relax the git-command check).
"""

import ast
from datetime import date
from pathlib import Path

from fdk_verification import run_release_candidate_check

from _fixtures import OK_COMMAND

_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "fdk_verification"

_ADVANCE_KEYWORDS = (
    "advance",
    "nextphase",
    "startnext",
    "continuetonext",
    "autocontinue",
    "triggernext",
    "proceedtonext",
)

_ALLOWED_GIT_PREFIXES = ("git status", "git diff", "git log", "git show", "git rev-parse")

_CONTRACT_PASSING = f"""\
## 1. Phase Metadata

- **Phase name:** 06
- **Phase objective:** prove the regression guard works

## 2. Required Tasks

- [x] T1: done

## 3. Acceptance Criteria

- [x] AC1: done

## 4. Expected File Scope

## 5. Required Validation Commands

- [x] Build: {OK_COMMAND}

## 6. Architecture Constraints

## 7. Documentation Requirements

## 8. Regression Targets

## 9. Required Verification Agents

- [x] Specification
- [x] Build
"""


def _all_source_files():
    return sorted(_PACKAGE_ROOT.rglob("*.py"))


def _defined_names(tree):
    names = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.append(target.id)
    return names


def _snapshot(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def _write_active_phase(root, sign_off_text="Not yet recorded — requires the project owner."):
    phase_dir = root / "forge-docs" / "implementation" / "Phase-06-Test"
    phase_dir.mkdir(parents=True)
    readme_text = (
        "# Test\n\n> **Status:** Implementation in progress\n\n"
        f"## Owner Sign-off\n\n{sign_off_text}\n"
    )
    (phase_dir / "README.md").write_text(readme_text, encoding="utf-8")
    (phase_dir / "VERIFICATION_CONTRACT.md").write_text(_CONTRACT_PASSING, encoding="utf-8")
    return phase_dir, readme_text


def test_no_advance_to_next_phase_symbol_exists_anywhere_in_the_source():
    matches = []
    for path in _all_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for name in _defined_names(tree):
            normalized = name.lower().replace("_", "")
            if any(keyword in normalized for keyword in _ADVANCE_KEYWORDS):
                matches.append(f"{path.relative_to(_PACKAGE_ROOT)}: {name}")

    assert matches == [], (
        "found a symbol shaped like phase-advancement -- this belongs to "
        f"Milestone 4B, not 4A: {matches}"
    )


def test_no_advance_to_next_phase_symbol_in_the_public_api():
    import fdk_verification

    offenders = [
        name
        for name in dir(fdk_verification)
        if any(keyword in name.lower().replace("_", "") for keyword in _ADVANCE_KEYWORDS)
    ]
    assert offenders == []


def test_no_mutating_git_command_is_constructed_anywhere_in_the_source():
    offenders = []
    for path in _all_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value.strip()
                if value.startswith("git ") and not any(
                    value.startswith(prefix) for prefix in _ALLOWED_GIT_PREFIXES
                ):
                    offenders.append(f"{path.relative_to(_PACKAGE_ROOT)}: {value!r}")

    assert offenders == [], f"found a git command outside the read-only allowlist: {offenders}"


def test_a_clean_pass_never_mutates_any_file_under_implementation(tmp_path):
    implementation_root = tmp_path / "forge-docs" / "implementation"
    _write_active_phase(tmp_path)
    before = _snapshot(implementation_root)

    outcome = run_release_candidate_check(tmp_path, today=date(2026, 7, 29))

    after = _snapshot(implementation_root)
    assert before == after, "no file under implementation/ may change, including on a clean PASS"
    assert outcome.repair_result.outcome.value == "PASSED"


def test_owner_sign_off_text_is_untouched_by_a_verification_run(tmp_path):
    phase_dir, readme_before = _write_active_phase(tmp_path)

    run_release_candidate_check(tmp_path, today=date(2026, 7, 29))

    assert (phase_dir / "README.md").read_text(encoding="utf-8") == readme_before


def test_verification_run_creates_no_git_refs_tags_or_commits(tmp_path):
    # Belt-and-suspenders companion to the source-level git-command scan
    # above: even if a command string slipped past that check, running the
    # pipeline against a real (but uncommitted) git repo must leave its
    # ref/tag state untouched -- this package only ever reads git state.
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _write_active_phase(tmp_path)
    refs_before = subprocess.run(
        ["git", "for-each-ref"], cwd=tmp_path, capture_output=True, text=True, check=True
    ).stdout

    run_release_candidate_check(tmp_path, today=date(2026, 7, 29))

    refs_after = subprocess.run(
        ["git", "for-each-ref"], cwd=tmp_path, capture_output=True, text=True, check=True
    ).stdout
    assert refs_before == refs_after
