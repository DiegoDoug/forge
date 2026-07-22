import zipfile
import io

import pytest

from app.schemas.project_init import AiInstructionsConfig, FdkPhaseConfig
from app.services.project_init import renderer
from app.services.project_init.zipper import to_zip


def test_render_fdk_phase_produces_all_twelve_files():
    config = FdkPhaseConfig(phase_number=9, phase_name="Knowledge Hub", objective="Unify Notes and Documents.")
    files = renderer.render_fdk_phase(config)

    assert len(files) == 13
    for filename in renderer.FDK_PHASE_FILES:
        assert f"Phase-09-Knowledge-Hub/{filename}" in files


def test_render_fdk_phase_substitutes_supplied_fields():
    config = FdkPhaseConfig(phase_number=9, phase_name="Knowledge Hub", objective="Unify Notes and Documents.")
    files = renderer.render_fdk_phase(config)

    readme = files["Phase-09-Knowledge-Hub/README.md"]
    assert "Knowledge Hub" in readme
    assert "Unify Notes and Documents." in readme
    assert "$phase_name" not in readme
    assert "$objective" not in readme


def test_render_fdk_phase_folder_name_pads_and_slugifies():
    assert renderer.phase_folder_name(3, "Prompt Studio") == "Phase-03-Prompt-Studio"
    assert renderer.phase_folder_name(12, "Weird!! Name??") == "Phase-12-Weird-Name"


def test_render_ai_instructions_produces_only_selected_files():
    config = AiInstructionsConfig(
        project_name="acme-api",
        description="An API for Acme.",
        tech_stack=["FastAPI", "Postgres"],
        conventions="Use snake_case.",
        output_files=["CLAUDE.md", "AGENTS.md"],
    )
    files = renderer.render_ai_instructions(config)

    assert set(files.keys()) == {"CLAUDE.md", "AGENTS.md"}
    assert "acme-api" in files["CLAUDE.md"]
    assert "FastAPI" in files["CLAUDE.md"]
    assert "Use snake_case." in files["CLAUDE.md"]
    assert "$project_name" not in files["CLAUDE.md"]


def test_render_ai_instructions_handles_empty_tech_stack_and_conventions():
    config = AiInstructionsConfig(
        project_name="bare-project",
        description="Nothing fancy.",
        output_files=["instructions.md"],
    )
    files = renderer.render_ai_instructions(config)

    content = files["instructions.md"]
    assert "(not specified)" in content
    assert "(none specified)" in content


def test_render_unknown_kind_raises_value_error():
    config = FdkPhaseConfig(phase_number=1, phase_name="Test", objective="Test.")
    with pytest.raises(ValueError):
        renderer.render("not_a_real_kind", config)


def test_zip_round_trips_filenames_and_content():
    files = {"a.txt": "hello", "dir/b.txt": "world"}
    zip_bytes = to_zip(files)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        assert set(archive.namelist()) == {"a.txt", "dir/b.txt"}
        assert archive.read("a.txt").decode("utf-8") == "hello"
        assert archive.read("dir/b.txt").decode("utf-8") == "world"
