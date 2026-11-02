"""Prompt Studio project scoping: additive ``project_id`` column on the
``prompts`` table so an authored prompt can optionally belong to a Project
(ADR-0014's organizational-label pattern, same as secrets/notes/documents in
0008). Purely additive - no existing column is modified.

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-01
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Guarded by column existence: on a fresh install 0001's
    # SQLModel.metadata.create_all() already builds `prompts` with this
    # column, so only pre-existing databases upgrading from before this
    # migration need it added here (matches 0008's convention).
    if "prompts" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("prompts")}
        if "project_id" not in columns:
            op.add_column("prompts", sa.Column("project_id", sa.String(), nullable=True))
            op.create_index("ix_prompts_project_id", "prompts", ["project_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "prompts" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("prompts")}
        if "project_id" in columns:
            # Explicit batch_alter_table - plain op.drop_column mis-recreates
            # an FK-bearing column's table on SQLite (see 0008's downgrade).
            with op.batch_alter_table("prompts") as batch_op:
                batch_op.drop_index("ix_prompts_project_id")
                batch_op.drop_column("project_id")
