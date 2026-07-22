from __future__ import annotations

from app.schemas.project_init import FieldSpec, TemplateCatalogOut, TemplateKindOut

from .renderer import AI_INSTRUCTIONS_FILES, FDK_PHASE_FILES

_CATALOG = TemplateCatalogOut(
    kinds=[
        TemplateKindOut(
            kind="fdk_phase",
            label="FDK Phase Scaffold",
            description="Generate a new Phase-XX-Name/ folder matching Forge's own FDK structure.",
            fields=[
                FieldSpec(name="phase_number", type="integer", required=True, min=1),
                FieldSpec(name="phase_name", type="string", required=True, max_length=80),
                FieldSpec(name="objective", type="string", required=True, max_length=500),
            ],
            output_files=list(FDK_PHASE_FILES),
        ),
        TemplateKindOut(
            kind="ai_instructions",
            label="AI Project Instructions",
            description="Generate CLAUDE.md / AGENTS.md / instructions.md for any project.",
            fields=[
                FieldSpec(name="project_name", type="string", required=True, max_length=80),
                FieldSpec(name="description", type="string", required=True, max_length=1000),
                FieldSpec(name="tech_stack", type="string[]", required=False, max_items=20),
                FieldSpec(name="conventions", type="string", required=False, max_length=4000),
                FieldSpec(
                    name="output_files",
                    type="string[]",
                    required=True,
                    enum=list(AI_INSTRUCTIONS_FILES),
                    min_items=1,
                ),
            ],
            output_files=None,
        ),
    ]
)


def get_catalog() -> TemplateCatalogOut:
    return _CATALOG
