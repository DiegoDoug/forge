from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from .base import new_id, utcnow


class ProviderCredential(SQLModel, table=True):
    """A user-configured API key for one LLM provider. Encrypted at rest with
    the same VaultCrypto primitive Secrets uses (see ADR-0010) - never
    decrypted except in-memory at the moment of an outbound call. One
    credential per provider (upsert on ``provider``), write-only after
    creation: no code path ever re-reads ``encrypted_api_key`` back out as
    plaintext for display."""

    __tablename__ = "provider_credentials"

    id: str = Field(default_factory=new_id, primary_key=True)
    provider: str = Field(index=True, unique=True, max_length=50)
    label: str = Field(max_length=200)
    encrypted_api_key: bytes
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class PlaygroundRun(SQLModel, table=True):
    """One prompt submitted to one or more provider/model targets."""

    __tablename__ = "playground_runs"

    id: str = Field(default_factory=new_id, primary_key=True)
    prompt: str = Field(max_length=20000)
    created_at: datetime = Field(default_factory=utcnow, index=True)

    results: list["PlaygroundResult"] = Relationship(
        back_populates="run",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "PlaygroundResult.created_at"},
    )


class PlaygroundResult(SQLModel, table=True):
    """One provider/model's outcome within a run. ``provider``/``model`` are
    plain string snapshots, not foreign keys to ProviderCredential - deleting
    a credential later must never orphan or corrupt past results (spec FR4,
    ADR-0010 SS2.4)."""

    __tablename__ = "playground_results"

    id: str = Field(default_factory=new_id, primary_key=True)
    run_id: str = Field(foreign_key="playground_runs.id", index=True)
    provider: str = Field(max_length=50)
    model: str = Field(max_length=100)
    status: str = Field(max_length=20)  # "success" | "error" | "timeout"
    response_text: str | None = Field(default=None, max_length=100000)
    error_message: str | None = Field(default=None, max_length=500)
    latency_ms: int | None = Field(default=None)
    prompt_tokens: int | None = Field(default=None)
    completion_tokens: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)

    run: PlaygroundRun = Relationship(back_populates="results")
