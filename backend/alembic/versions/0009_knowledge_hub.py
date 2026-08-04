"""Knowledge Hub: note_tag_links, document_tag_links (both referencing the
existing tags table), and knowledge_links (polymorphic note/document link).
Purely additive - no existing table or column is modified. See ADR-0015 and
forge-docs/implementation/Phase-07-Knowledge-Hub/04_DATABASE.md.

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-04
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = inspector.get_table_names()

    # On a fresh install, 0001's SQLModel.metadata.create_all() already
    # creates these tables (registered in app/models/__init__.py by the time
    # 0001 runs) - only pre-existing databases upgrading from before this
    # migration actually need them created here, matching 0008's convention.
    if "note_tag_links" not in existing:
        op.create_table(
            "note_tag_links",
            sa.Column("note_id", sa.String(), sa.ForeignKey("notes.id"), primary_key=True),
            sa.Column("tag_id", sa.String(), sa.ForeignKey("tags.id"), primary_key=True),
        )

    if "document_tag_links" not in existing:
        op.create_table(
            "document_tag_links",
            sa.Column("document_id", sa.String(), sa.ForeignKey("documents.id"), primary_key=True),
            sa.Column("tag_id", sa.String(), sa.ForeignKey("tags.id"), primary_key=True),
        )

    if "knowledge_links" not in existing:
        op.create_table(
            "knowledge_links",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("source_type", sa.String(length=10), nullable=False),
            sa.Column("source_id", sa.String(length=64), nullable=False),
            sa.Column("target_type", sa.String(length=10), nullable=False),
            sa.Column("target_id", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "source_type", "source_id", "target_type", "target_id", name="uq_knowledge_links_pair"
            ),
        )
        op.create_index("ix_knowledge_links_source", "knowledge_links", ["source_type", "source_id"])
        op.create_index("ix_knowledge_links_target", "knowledge_links", ["target_type", "target_id"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_links_target", table_name="knowledge_links")
    op.drop_index("ix_knowledge_links_source", table_name="knowledge_links")
    op.drop_table("knowledge_links")
    op.drop_table("document_tag_links")
    op.drop_table("note_tag_links")
