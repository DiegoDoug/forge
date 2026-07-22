from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from .base import new_id, utcnow


class Prompt(SQLModel, table=True):
    """An authored, versioned LLM prompt. ``variables_json``/``tags_json`` are
    JSON-encoded lists, validated at the Pydantic boundary (see
    schemas/prompt_studio.py) - same pattern as ProjectInitGeneration.config."""

    __tablename__ = "prompts"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(index=True, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    body: str = Field(max_length=20000)
    variables_json: str = Field(default="[]")
    tags_json: str = Field(default="[]")
    version_number: int = Field(default=1)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    versions: list["PromptVersion"] = Relationship(
        back_populates="prompt",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "PromptVersion.created_at.desc()"},
    )


class PromptVersion(SQLModel, table=True):
    """Immutable snapshot of a prompt's body/variables, written whenever
    either changes. Mirrors SecretVersion's snapshot-before-overwrite shape."""

    __tablename__ = "prompt_versions"

    id: str = Field(default_factory=new_id, primary_key=True)
    prompt_id: str = Field(foreign_key="prompts.id", index=True)
    version_number: int
    body: str = Field(max_length=20000)
    variables_json: str = Field(default="[]")
    note: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=utcnow, index=True)

    prompt: Prompt = Relationship(back_populates="versions")
