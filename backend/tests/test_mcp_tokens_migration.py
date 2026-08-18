from __future__ import annotations

import os
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Hand-written DDL matching activity_log exactly as it existed right before
# 0010 (no `source` column) - mirrors test_projects_migration.py's approach
# of building only the table(s) the migration under test actually touches,
# not the full historical schema, since Alembic doesn't inspect actual
# tables for migrations that don't reference them.
_PRE_0010_ACTIVITY_LOG_DDL = """CREATE TABLE activity_log (
    id VARCHAR NOT NULL PRIMARY KEY,
    action VARCHAR NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    summary VARCHAR(300) NOT NULL,
    created_at DATETIME NOT NULL
)"""


def _alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return cfg


def test_0010_mcp_tokens_upgrade_preserves_existing_activity_rows_and_downgrade_upgrade_cycle_is_clean():
    from app.core.config import get_settings

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    tmp_dir = tempfile.mkdtemp(prefix="forge-mcp-migration-test-")
    os.environ["FORGE_DATA_DIR"] = tmp_dir
    get_settings.cache_clear()

    try:
        db_path = Path(tmp_dir) / "forge.db"
        cfg = _alembic_config()

        engine = sa.create_engine(f"sqlite:///{db_path}")
        with engine.begin() as conn:
            conn.execute(sa.text(_PRE_0010_ACTIVITY_LOG_DDL))
            conn.execute(
                sa.text(
                    "INSERT INTO activity_log (id, action, entity_type, entity_id, summary, created_at) "
                    "VALUES ('act1', 'created', 'note', 'note1', 'pre-existing activity row', '2026-01-01')"
                )
            )
        engine.dispose()
        command.stamp(cfg, "0009")

        command.upgrade(cfg, "head")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "mcp_tokens" in inspector.get_table_names()
        mcp_token_columns = {c["name"] for c in inspector.get_columns("mcp_tokens")}
        assert mcp_token_columns == {
            "id",
            "name",
            "token_hash",
            "scopes",
            "created_at",
            "last_used_at",
            "revoked_at",
        }
        activity_columns = {c["name"] for c in inspector.get_columns("activity_log")}
        assert "source" in activity_columns

        with engine.connect() as conn:
            summary = conn.execute(sa.text("SELECT summary FROM activity_log WHERE id = 'act1'")).scalar_one()
            assert summary == "pre-existing activity row"
            source = conn.execute(sa.text("SELECT source FROM activity_log WHERE id = 'act1'")).scalar_one()
            assert source == "ui", "pre-existing rows must backfill to the 'ui' default, not NULL"
        engine.dispose()

        # Downgrade one step, then upgrade again - must be clean and lossless.
        command.downgrade(cfg, "0009")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "mcp_tokens" not in inspector.get_table_names()
        activity_columns = {c["name"] for c in inspector.get_columns("activity_log")}
        assert "source" not in activity_columns
        with engine.connect() as conn:
            summary = conn.execute(sa.text("SELECT summary FROM activity_log WHERE id = 'act1'")).scalar_one()
            assert summary == "pre-existing activity row"
        engine.dispose()

        command.upgrade(cfg, "head")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "mcp_tokens" in inspector.get_table_names()
        with engine.connect() as conn:
            summary = conn.execute(sa.text("SELECT summary FROM activity_log WHERE id = 'act1'")).scalar_one()
            assert summary == "pre-existing activity row"
        engine.dispose()
    finally:
        if previous_data_dir is None:
            os.environ.pop("FORGE_DATA_DIR", None)
        else:
            os.environ["FORGE_DATA_DIR"] = previous_data_dir
        get_settings.cache_clear()


def test_running_0010_twice_on_a_fresh_install_is_a_no_op():
    """On a fresh install, 0001's SQLModel.metadata.create_all() already
    creates mcp_tokens and the source column - 0010 must detect that and do
    nothing, not error or duplicate anything (matches 0008/0009's own
    fresh-install idempotency tests implicitly exercised by every other
    migration test's use of command.upgrade(cfg, "head") from empty)."""
    from app.core.config import get_settings

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    tmp_dir = tempfile.mkdtemp(prefix="forge-mcp-migration-fresh-test-")
    os.environ["FORGE_DATA_DIR"] = tmp_dir
    get_settings.cache_clear()

    try:
        cfg = _alembic_config()
        command.upgrade(cfg, "head")  # fresh install: 0001's create_all already has everything

        db_path = Path(tmp_dir) / "forge.db"
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "mcp_tokens" in inspector.get_table_names()
        assert "source" in {c["name"] for c in inspector.get_columns("activity_log")}
        engine.dispose()
    finally:
        if previous_data_dir is None:
            os.environ.pop("FORGE_DATA_DIR", None)
        else:
            os.environ["FORGE_DATA_DIR"] = previous_data_dir
        get_settings.cache_clear()
