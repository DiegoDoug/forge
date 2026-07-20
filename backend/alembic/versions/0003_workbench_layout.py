"""Workbench: workbench_layout table (single-row instance-wide layout config).

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates `workbench_layout` (the model is registered in
    # app/models/__init__.py by the time 0001 runs) — only pre-existing
    # databases upgrading from before this migration actually need the table
    # created here. No data migration: the row is created lazily on first
    # access via get-or-create in `get_layout()`.
    if "workbench_layout" not in inspector.get_table_names():
        op.create_table(
            "workbench_layout",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("panels", sa.String(), nullable=False, server_default="[]"),
            sa.Column("pinned_tools", sa.String(), nullable=False, server_default="[]"),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("workbench_layout")
