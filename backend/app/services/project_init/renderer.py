from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from string import Template

from app.schemas.project_init import AiInstructionsConfig, FdkPhaseConfig

_TEMPLATES_ROOT = Path(__file__).resolve().parent / "templates"

FDK_PHASE_FILES = [
    "README.md",
    "CURRENT_STATE.md",
    "01_SPEC.md",
    "02_UI.md",
    "03_BACKEND.md",
    "04_DATABASE.md",
    "05_COMPONENTS.md",
    "06_API.md",
    "07_TESTING.md",
    "08_ACCEPTANCE.md",
    "09_IMPLEMENTATION_TASKS.md",
    "10_RELEASE_NOTES.md",
    "IMPLEMENT.md",
]

AI_INSTRUCTIONS_FILES = ["CLAUDE.md", "AGENTS.md", "instructions.md"]

_SLUG_UNSAFE = re.compile(r"[^A-Za-z0-9]+")


def _slug(text: str) -> str:
    cleaned = _SLUG_UNSAFE.sub("-", text.strip()).strip("-")
    return cleaned or "Untitled"


def phase_folder_name(phase_number: int, phase_name: str) -> str:
    return f"Phase-{phase_number:02d}-{_slug(phase_name)}"


def project_slug(project_name: str) -> str:
    return _slug(project_name).lower()


def _load_template(relative_path: str) -> str:
    return (_TEMPLATES_ROOT / relative_path).read_text(encoding="utf-8")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _tech_stack_bullets(tech_stack: list[str]) -> str:
    if not tech_stack:
        return "- (not specified)"
    return "\n".join(f"- {item}" for item in tech_stack)


def _conventions_section(conventions: str) -> str:
    return conventions.strip() or "(none specified)"


def render_fdk_phase(config: FdkPhaseConfig) -> dict[str, str]:
    mapping = {
        "phase_name": config.phase_name,
        "phase_number": str(config.phase_number),
        "objective": config.objective,
        "generated_date": _today(),
    }
    folder = phase_folder_name(config.phase_number, config.phase_name)
    files: dict[str, str] = {}
    for filename in FDK_PHASE_FILES:
        template_text = _load_template(f"fdk_phase/{filename}.tmpl")
        files[f"{folder}/{filename}"] = Template(template_text).substitute(mapping)
    return files


def render_ai_instructions(config: AiInstructionsConfig) -> dict[str, str]:
    mapping = {
        "project_name": config.project_name,
        "description": config.description,
        "tech_stack_bullets": _tech_stack_bullets(config.tech_stack),
        "conventions_section": _conventions_section(config.conventions),
        "generated_date": _today(),
    }
    files: dict[str, str] = {}
    for filename in config.output_files:
        template_text = _load_template(f"ai_instructions/{filename}.tmpl")
        files[filename] = Template(template_text).substitute(mapping)
    return files


def render(kind: str, config: FdkPhaseConfig | AiInstructionsConfig) -> dict[str, str]:
    if kind == "fdk_phase" and isinstance(config, FdkPhaseConfig):
        return render_fdk_phase(config)
    if kind == "ai_instructions" and isinstance(config, AiInstructionsConfig):
        return render_ai_instructions(config)
    raise ValueError(f"Unknown template kind or config mismatch: {kind}")
