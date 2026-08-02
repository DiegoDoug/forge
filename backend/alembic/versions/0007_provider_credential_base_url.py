"""Model Playground: add nullable base_url to provider_credentials (ADR-0013).

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-02
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # On a fresh install, 0001's `SQLModel.metadata.create_all()` already
    # creates this column (registered on the model by the time 0001 runs) -
    # only pre-existing databases upgrading from before this migration
    # actually need it added here.
    columns = {c["name"] for c in inspector.get_columns("provider_credentials")}
    if "base_url" not in columns:
        op.add_column("provider_credentials", sa.Column("base_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("provider_credentials", "base_url")
