"""Documents tab: documents table + FTS5 search index.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-17
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates `documents` (the model is registered in app/models/__init__.py
    # by the time 0001 runs) — only pre-existing databases upgrading from
    # before this migration actually need the table created here.
    if "documents" not in inspector.get_table_names():
        op.create_table(
            "documents",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("title", sa.String(length=200), nullable=False, server_default=""),
            sa.Column("content", sa.Text(), nullable=False, server_default=""),
            sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_documents_pinned", "documents", ["pinned"])
        op.create_index("ix_documents_updated_at", "documents", ["updated_at"])

    # FTS5 external-content index, kept in sync via triggers — same approach
    # as the notes_fts index from the initial migration.
    op.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5("
        "title, content, content='documents', content_rowid='rowid')"
    )
    op.execute(
        "INSERT INTO documents_fts(rowid, title, content) SELECT rowid, title, content FROM documents"
    )
    op.execute(
        "CREATE TRIGGER documents_ai AFTER INSERT ON documents BEGIN "
        "INSERT INTO documents_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content); "
        "END"
    )
    op.execute(
        "CREATE TRIGGER documents_ad AFTER DELETE ON documents BEGIN "
        "INSERT INTO documents_fts(documents_fts, rowid, title, content) VALUES('delete', old.rowid, old.title, old.content); "
        "END"
    )
    op.execute(
        "CREATE TRIGGER documents_au AFTER UPDATE ON documents BEGIN "
        "INSERT INTO documents_fts(documents_fts, rowid, title, content) VALUES('delete', old.rowid, old.title, old.content); "
        "INSERT INTO documents_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content); "
        "END"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS documents_au")
    op.execute("DROP TRIGGER IF EXISTS documents_ad")
    op.execute("DROP TRIGGER IF EXISTS documents_ai")
    op.execute("DROP TABLE IF EXISTS documents_fts")
    op.drop_index("ix_documents_updated_at", table_name="documents")
    op.drop_index("ix_documents_pinned", table_name="documents")
    op.drop_table("documents")
