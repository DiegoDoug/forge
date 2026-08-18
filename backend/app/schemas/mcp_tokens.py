from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# The full scope vocabulary (01_SPEC.md SS4.4). forge:secrets is a valid,
# storable scope value - reserved for a future milestone - but no MCP tool
# in this phase checks for it. Provisioning an all-zero-scope token is
# allowed (e.g. a token meant only to prove connectivity); it simply cannot
# do anything once connected.
VALID_MCP_SCOPES = {"forge:read", "forge:write", "forge:delete", "forge:secrets"}


class McpTokenCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scopes: list[str] = Field(default_factory=list)

    @field_validator("scopes")
    @classmethod
    def _validate_scopes(cls, value: list[str]) -> list[str]:
        unknown = sorted(set(value) - VALID_MCP_SCOPES)
        if unknown:
            raise ValueError(f"Unknown MCP scope(s): {', '.join(unknown)}")
        return value


class McpTokenOut(BaseModel):
    """Never includes token_hash or the raw token - metadata only, per
    01_SPEC.md SS4.3.1."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    scopes: list[str]
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None

    @classmethod
    def from_model(cls, token) -> "McpTokenOut":
        scopes = sorted(s.strip() for s in token.scopes.split(",") if s.strip())
        return cls(
            id=token.id,
            name=token.name,
            scopes=scopes,
            created_at=token.created_at,
            last_used_at=token.last_used_at,
            revoked_at=token.revoked_at,
        )


class McpTokenCreatedOut(McpTokenOut):
    """Returned exactly once, at creation time - the only response shape
    that ever carries the raw token value."""

    token: str
