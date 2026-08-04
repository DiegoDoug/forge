"""Projects: new projects table, plus additive project_id on secrets, notes,
documents, and playground_runs (ADR-0014).

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-02
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CHILD_TABLES = ("secrets", "notes", "documents", "playground_runs")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates this table (registered in app/models/__init__.py by the time
    # 0001 runs) - only pre-existing databases upgrading from before this
    # migration actually need the table created here.
    if "projects" not in inspector.get_table_names():
        op.create_table(
            "projects",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.String(length=2000), nullable=False),
            sa.Column("color", sa.String(length=20), nullable=False),
            sa.Column("archived", sa.Boolean(), nullable=False),
            sa.Column("default_provider", sa.String(length=50), nullable=True),
            sa.Column("default_model", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_projects_name", "projects", ["name"])
        op.create_index("ix_projects_archived", "projects", ["archived"])

    for table in _CHILD_TABLES:
        columns = {c["name"] for c in inspector.get_columns(table)}
        if "project_id" not in columns:
            op.add_column(table, sa.Column("project_id", sa.String(), nullable=True))
            op.create_index(f"ix_{table}_project_id", table, ["project_id"])


def downgrade() -> None:
    for table in reversed(_CHILD_TABLES):
        # A plain op.drop_column on SQLite silently mis-recreates the table
        # when the dropped column carries a FK constraint (fresh installs get
        # a real `FOREIGN KEY(project_id) REFERENCES projects(id)` from
        # SQLModel.metadata.create_all in 0001) - explicit batch_alter_table
        # is the documented-reliable way to drop an FK-bearing column on
        # SQLite; plain op.drop_index/op.drop_column can leave a stale FK
        # reference to the now-gone column in the recreated table.
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_index(f"ix_{table}_project_id")
            batch_op.drop_column("project_id")

    op.drop_index("ix_projects_archived", table_name="projects")
    op.drop_index("ix_projects_name", table_name="projects")
    op.drop_table("projects")
