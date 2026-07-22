"""Prompt Studio: prompts, prompt_versions tables.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-22
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates both tables (Prompt/PromptVersion are registered in
    # app/models/__init__.py by the time 0001 runs) - only pre-existing
    # databases upgrading from before this migration actually need the
    # tables created here.
    if "prompts" not in inspector.get_table_names():
        op.create_table(
            "prompts",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.String(length=1000), nullable=True),
            sa.Column("body", sa.String(length=20000), nullable=False),
            sa.Column("variables_json", sa.String(), nullable=False, server_default="[]"),
            sa.Column("tags_json", sa.String(), nullable=False, server_default="[]"),
            sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_prompts_name", "prompts", ["name"])

    if "prompt_versions" not in inspector.get_table_names():
        op.create_table(
            "prompt_versions",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("prompt_id", sa.String(), sa.ForeignKey("prompts.id"), nullable=False),
            sa.Column("version_number", sa.Integer(), nullable=False),
            sa.Column("body", sa.String(length=20000), nullable=False),
            sa.Column("variables_json", sa.String(), nullable=False, server_default="[]"),
            sa.Column("note", sa.String(length=200), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_prompt_versions_prompt_id", "prompt_versions", ["prompt_id"])
        op.create_index("ix_prompt_versions_created_at", "prompt_versions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_prompt_versions_created_at", table_name="prompt_versions")
    op.drop_index("ix_prompt_versions_prompt_id", table_name="prompt_versions")
    op.drop_table("prompt_versions")
    op.drop_index("ix_prompts_name", table_name="prompts")
    op.drop_table("prompts")
