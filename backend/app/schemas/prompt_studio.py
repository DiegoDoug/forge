from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.prompt_studio.templating import extract_placeholders

VARIABLE_NAME_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]{0,63}$"
MAX_VARIABLES = 50
MAX_TAGS = 10


class PromptVariableIn(BaseModel):
    name: str = Field(pattern=VARIABLE_NAME_PATTERN)
    type: Literal["string", "number", "boolean"]
    required: bool = True
    default: str | float | bool | None = None
    description: str | None = Field(default=None, max_length=500)


class PromptVariableOut(PromptVariableIn):
    model_config = ConfigDict(from_attributes=True)


def _validate_variables(variables: list[PromptVariableIn]) -> list[PromptVariableIn]:
    if len(variables) > MAX_VARIABLES:
        raise ValueError(f"A prompt may declare at most {MAX_VARIABLES} variables")
    names = [v.name for v in variables]
    if len(names) != len(set(names)):
        raise ValueError("Variable names must be unique within a prompt")
    return variables


def _validate_body_placeholders(body: str, variables: list[PromptVariableIn]) -> None:
    declared = {v.name for v in variables}
    referenced = extract_placeholders(body)
    undeclared = referenced - declared
    if undeclared:
        raise ValueError(f"Body references undeclared variable(s): {', '.join(sorted(undeclared))}")


def _validate_tags(tags: list[str]) -> list[str]:
    if len(tags) > MAX_TAGS:
        raise ValueError(f"A prompt may have at most {MAX_TAGS} tags")
    for tag in tags:
        if len(tag) > 30:
            raise ValueError("Each tag must be at most 30 characters")
    return tags


class PromptCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    body: str = Field(min_length=1, max_length=20000)
    variables: list[PromptVariableIn] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @field_validator("variables")
    @classmethod
    def _check_variables(cls, v: list[PromptVariableIn]) -> list[PromptVariableIn]:
        return _validate_variables(v)

    @field_validator("tags")
    @classmethod
    def _check_tags(cls, v: list[str]) -> list[str]:
        return _validate_tags(v)

    @model_validator(mode="after")
    def _check_body_placeholders(self) -> "PromptCreate":
        _validate_body_placeholders(self.body, self.variables)
        return self


class PromptUpdateMeta(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    tags: list[str] | None = None

    @field_validator("tags")
    @classmethod
    def _check_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        return _validate_tags(v)


class PromptUpdateContent(BaseModel):
    body: str = Field(min_length=1, max_length=20000)
    variables: list[PromptVariableIn] = Field(default_factory=list)

    @field_validator("variables")
    @classmethod
    def _check_variables(cls, v: list[PromptVariableIn]) -> list[PromptVariableIn]:
        return _validate_variables(v)

    @model_validator(mode="after")
    def _check_body_placeholders(self) -> "PromptUpdateContent":
        _validate_body_placeholders(self.body, self.variables)
        return self


class PromptOut(BaseModel):
    id: str
    name: str
    description: str | None
    body: str
    variables: list[PromptVariableOut]
    tags: list[str]
    version_number: int
    created_at: datetime
    updated_at: datetime


class PromptListItemOut(BaseModel):
    id: str
    name: str
    description: str | None
    tags: list[str]
    version_number: int
    updated_at: datetime


class PromptListOut(BaseModel):
    items: list[PromptListItemOut]


class PromptVersionOut(BaseModel):
    id: str
    version_number: int
    body: str
    variables: list[PromptVariableOut]
    note: str | None
    created_at: datetime


class PromptVersionListItemOut(BaseModel):
    id: str
    version_number: int
    note: str | None
    created_at: datetime


class PromptVersionListOut(BaseModel):
    items: list[PromptVersionListItemOut]
