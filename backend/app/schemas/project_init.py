from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AiInstructionsFile = Literal["CLAUDE.md", "AGENTS.md", "instructions.md"]


class FieldSpec(BaseModel):
    name: str
    type: str
    required: bool
    max_length: int | None = None
    min: int | None = None
    max_items: int | None = None
    min_items: int | None = None
    enum: list[str] | None = None


class TemplateKindOut(BaseModel):
    kind: str
    label: str
    description: str
    fields: list[FieldSpec]
    output_files: list[str] | None = None


class TemplateCatalogOut(BaseModel):
    kinds: list[TemplateKindOut]


class FdkPhaseConfig(BaseModel):
    phase_number: int = Field(ge=1)
    phase_name: str = Field(min_length=1, max_length=80)
    objective: str = Field(min_length=1, max_length=500)


class AiInstructionsConfig(BaseModel):
    project_name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=1000)
    tech_stack: list[str] = Field(default_factory=list, max_length=20)
    conventions: str = Field(default="", max_length=4000)
    output_files: list[AiInstructionsFile] = Field(min_length=1)


class GenerateRequest(BaseModel):
    kind: Literal["fdk_phase", "ai_instructions"]
    config: dict


class GenerationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    name: str
    created_at: datetime
    file_count: int


class GenerationListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    name: str
    created_at: datetime


class GenerationListOut(BaseModel):
    items: list[GenerationListItemOut]
