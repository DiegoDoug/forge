"""Phase 11 (Claude MCP / Second Brain), Milestone 1: mcp_tokens table for
individually-revocable MCP bearer credentials (ADR-0019), plus an additive
`source` column on activity_log distinguishing MCP-originated writes from
UI-originated ones. Purely additive - no existing table or column is
modified beyond the new activity_log column. See
forge-docs/implementation/Phase-11-Claude-MCP/04_DATABASE.md.

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-18
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's SQLModel.metadata.create_all() already
    # creates this table (registered in app/models/__init__.py by the time
    # 0001 runs) - only pre-existing databases upgrading from before this
    # migration actually need it created here, matching 0008/0009's convention.
    if "mcp_tokens" not in inspector.get_table_names():
        op.create_table(
            "mcp_tokens",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("token_hash", sa.String(), nullable=False),
            sa.Column("scopes", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_mcp_tokens_token_hash", "mcp_tokens", ["token_hash"])

    # Guarded by table existence, not just column existence: every real
    # install has activity_log by the time this migration runs (0001 creates
    # it unconditionally), but a migration test fixture stamped at an
    # earlier revision and hand-building only the tables its own migration
    # touches (e.g. test_projects_migration.py, test_knowledge_migration.py)
    # legitimately may not include it. Skipping cleanly here, rather than
    # requiring every such fixture to grow an unrelated table, keeps this
    # migration's own correctness (real installs always have the table)
    # from leaking into an assumption about what every synthetic test
    # database contains.
    if "activity_log" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("activity_log")}
        if "source" not in columns:
            op.add_column(
                "activity_log",
                sa.Column("source", sa.String(length=20), nullable=False, server_default="ui"),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "activity_log" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("activity_log")}
        if "source" in columns:
            with op.batch_alter_table("activity_log") as batch_op:
                batch_op.drop_column("source")

    op.drop_index("ix_mcp_tokens_token_hash", table_name="mcp_tokens")
    op.drop_table("mcp_tokens")
