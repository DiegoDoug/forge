from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from .base import new_id, utcnow


class McpToken(SQLModel, table=True):
    """A persistent, individually-revocable credential for the MCP server
    (Phase 11). Never confused with the bootstrap credential
    (FORGE_MCP_BOOTSTRAP_TOKEN), which authenticates provisioning only and is
    never stored here - see ADR-0019.

    ``token_hash`` is a salted hash; the raw token is generated once, shown
    once to the caller of POST /api/mcp/tokens, and never persisted or
    logged - mirroring how AppConfig.master_password_hash never stores the
    master password itself.
    """

    __tablename__ = "mcp_tokens"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(max_length=100)
    token_hash: str = Field(index=True)
    scopes: str
    created_at: datetime = Field(default_factory=utcnow)
    last_used_at: datetime | None = Field(default=None)
    revoked_at: datetime | None = Field(default=None)
