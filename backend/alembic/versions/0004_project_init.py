"""Project Init: project_init_generations table.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-22
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates `project_init_generations` (the model is registered in
    # app/models/__init__.py by the time 0001 runs) — only pre-existing
    # databases upgrading from before this migration actually need the table
    # created here.
    if "project_init_generations" not in inspector.get_table_names():
        op.create_table(
            "project_init_generations",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("kind", sa.String(length=32), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("config", sa.String(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_project_init_generations_kind", "project_init_generations", ["kind"])
        op.create_index("ix_project_init_generations_created_at", "project_init_generations", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_project_init_generations_created_at", table_name="project_init_generations")
    op.drop_index("ix_project_init_generations_kind", table_name="project_init_generations")
    op.drop_table("project_init_generations")
