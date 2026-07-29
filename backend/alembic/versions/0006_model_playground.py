"""Model Playground: provider_credentials, playground_runs, playground_results tables.

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-29
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates these tables (they're registered in app/models/__init__.py by
    # the time 0001 runs) - only pre-existing databases upgrading from before
    # this migration actually need the tables created here.
    if "provider_credentials" not in inspector.get_table_names():
        op.create_table(
            "provider_credentials",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("label", sa.String(length=200), nullable=False),
            sa.Column("encrypted_api_key", sa.LargeBinary(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_provider_credentials_provider", "provider_credentials", ["provider"], unique=True
        )

    if "playground_runs" not in inspector.get_table_names():
        op.create_table(
            "playground_runs",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("prompt", sa.String(length=20000), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_playground_runs_created_at", "playground_runs", ["created_at"])

    if "playground_results" not in inspector.get_table_names():
        op.create_table(
            "playground_results",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("run_id", sa.String(), sa.ForeignKey("playground_runs.id"), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("model", sa.String(length=100), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("response_text", sa.String(length=100000), nullable=True),
            sa.Column("error_message", sa.String(length=500), nullable=True),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("prompt_tokens", sa.Integer(), nullable=True),
            sa.Column("completion_tokens", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_playground_results_run_id", "playground_results", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_playground_results_run_id", table_name="playground_results")
    op.drop_table("playground_results")
    op.drop_index("ix_playground_runs_created_at", table_name="playground_runs")
    op.drop_table("playground_runs")
    op.drop_index("ix_provider_credentials_provider", table_name="provider_credentials")
    op.drop_table("provider_credentials")
