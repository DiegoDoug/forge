from __future__ import annotations

import os
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Hand-written DDL matching the schema exactly as it existed at migration
# 0007 (secrets/notes/documents columns per 0001's SQLModel.metadata.create_all
# at that point in history; playground_runs per 0006's explicit op.create_table)
# - deliberately NOT using command.upgrade(cfg, "0007") to build this fixture,
# because 0001 always runs SQLModel.metadata.create_all() against the
# *current* (Phase-06-including) models, which would create project_id
# columns from the start and never exercise 0008's real op.add_column path.
# This mirrors what a genuine pre-existing installation's database looks like
# the moment before it's upgraded past 0007.
_PRE_0008_DDL = [
    """CREATE TABLE secrets (
        id VARCHAR NOT NULL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        type VARCHAR NOT NULL,
        folder_id VARCHAR,
        encrypted_value BLOB NOT NULL,
        encrypted_metadata BLOB,
        favorite BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )""",
    """CREATE TABLE notes (
        id VARCHAR NOT NULL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content VARCHAR NOT NULL,
        color VARCHAR(20) NOT NULL,
        pos_x FLOAT NOT NULL,
        pos_y FLOAT NOT NULL,
        width FLOAT NOT NULL,
        height FLOAT NOT NULL,
        z_index INTEGER NOT NULL,
        pinned BOOLEAN NOT NULL,
        archived BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )""",
    """CREATE TABLE documents (
        id VARCHAR NOT NULL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content VARCHAR NOT NULL,
        pinned BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )""",
    """CREATE TABLE playground_runs (
        id VARCHAR NOT NULL PRIMARY KEY,
        prompt VARCHAR(20000) NOT NULL,
        created_at DATETIME NOT NULL
    )""",
]


def _alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return cfg


def test_0008_projects_upgrade_preserves_existing_data_and_downgrade_upgrade_cycle_is_clean():
    # alembic/env.py always resolves its own sqlalchemy.url from
    # get_settings().sync_database_url (FORGE_DATA_DIR-derived), ignoring any
    # url passed on the Config object - so isolation here means pointing
    # FORGE_DATA_DIR at a throwaway directory and clearing the settings
    # lru_cache, the same pattern every *_api.py test module already uses.
    from app.core.config import get_settings

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    tmp_dir = tempfile.mkdtemp(prefix="forge-migration-test-")
    os.environ["FORGE_DATA_DIR"] = tmp_dir
    get_settings.cache_clear()

    try:
        db_path = Path(tmp_dir) / "forge.db"
        cfg = _alembic_config()

        # Build the database exactly as it looked right before 0008, then
        # tell alembic it's already at 0007 (stamp, not upgrade) so the real
        # upgrade() below exercises 0008's actual op.create_table/add_column
        # path against genuinely pre-existing tables/data.
        engine = sa.create_engine(f"sqlite:///{db_path}")
        with engine.begin() as conn:
            for ddl in _PRE_0008_DDL:
                conn.execute(sa.text(ddl))
            conn.execute(
                sa.text(
                    "INSERT INTO secrets (id, name, type, encrypted_value, favorite, created_at, updated_at) "
                    "VALUES ('sec1', 'pre-existing secret', 'other', X'00', 0, '2026-01-01', '2026-01-01')"
                )
            )
            conn.execute(
                sa.text(
                    "INSERT INTO notes (id, title, content, color, pos_x, pos_y, width, height, z_index, "
                    "pinned, archived, created_at, updated_at) "
                    "VALUES ('note1', 'pre-existing note', '', '#fde68a', 0, 0, 280, 220, 0, 0, 0, "
                    "'2026-01-01', '2026-01-01')"
                )
            )
        engine.dispose()
        command.stamp(cfg, "0007")

        # Upgrade to head (0008) - the migration under test, against a
        # genuinely pre-0008 schema.
        command.upgrade(cfg, "head")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "projects" in inspector.get_table_names()
        for table in ("secrets", "notes", "documents", "playground_runs"):
            columns = {c["name"] for c in inspector.get_columns(table)}
            assert "project_id" in columns

        with engine.connect() as conn:
            name = conn.execute(sa.text("SELECT name FROM secrets WHERE id = 'sec1'")).scalar_one()
            assert name == "pre-existing secret"
            project_id = conn.execute(sa.text("SELECT project_id FROM secrets WHERE id = 'sec1'")).scalar_one()
            assert project_id is None
            title = conn.execute(sa.text("SELECT title FROM notes WHERE id = 'note1'")).scalar_one()
            assert title == "pre-existing note"
        engine.dispose()

        # Downgrade one step, then upgrade again - must be clean and lossless
        # for the pre-existing rows.
        command.downgrade(cfg, "0007")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "projects" not in inspector.get_table_names()
        columns = {c["name"] for c in inspector.get_columns("secrets")}
        assert "project_id" not in columns
        with engine.connect() as conn:
            name = conn.execute(sa.text("SELECT name FROM secrets WHERE id = 'sec1'")).scalar_one()
            assert name == "pre-existing secret"
        engine.dispose()

        command.upgrade(cfg, "head")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "projects" in inspector.get_table_names()
        with engine.connect() as conn:
            name = conn.execute(sa.text("SELECT name FROM secrets WHERE id = 'sec1'")).scalar_one()
            assert name == "pre-existing secret"
            title = conn.execute(sa.text("SELECT title FROM notes WHERE id = 'note1'")).scalar_one()
            assert title == "pre-existing note"
        engine.dispose()
    finally:
        if previous_data_dir is None:
            os.environ.pop("FORGE_DATA_DIR", None)
        else:
            os.environ["FORGE_DATA_DIR"] = previous_data_dir
        get_settings.cache_clear()
