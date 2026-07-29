import subprocess

import pytest

from fdk_verification import ChecklistItem, VerificationContract


def _checklist(*pairs):
    return [ChecklistItem(text=text, checked=checked) for text, checked in pairs]


@pytest.fixture
def checklist():
    return _checklist


@pytest.fixture
def make_contract():
    def _make(**overrides):
        defaults = dict(
            phase_name="05",
            phase_objective="",
            dependencies="",
            completion_definition="",
            required_tasks=[],
            acceptance_criteria=[],
            expected_scope="",
            out_of_scope="",
            required_validation_commands=[],
            architecture_constraints=[],
            documentation_requirements=[],
            regression_targets=[],
            verifier_declarations=[],
        )
        defaults.update(overrides)
        return VerificationContract(**defaults)

    return _make


@pytest.fixture
def git_repo(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path
