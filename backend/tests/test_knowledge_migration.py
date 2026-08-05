from __future__ import annotations

import os
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Hand-written DDL matching the schema exactly as it existed at migration
# 0008 (notes/tags only - the subset this test needs) - deliberately NOT
# built by running the real chain from empty, because 0001 always runs
# SQLModel.metadata.create_all() against the *current* models (which now
# include note_tag_links/document_tag_links/knowledge_links), which would
# create this migration's tables from the start and never exercise 0009's
# real op.create_table path. Same reasoning as test_projects_migration.py's
# _PRE_0008_DDL.
_PRE_0009_DDL = [
    """CREATE TABLE notes (
        id VARCHAR NOT NULL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content VARCHAR NOT NULL,
        color VARCHAR(20) NOT NULL,
        project_id VARCHAR,
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
        project_id VARCHAR,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )""",
    """CREATE TABLE tags (
        id VARCHAR NOT NULL PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        color VARCHAR(20) NOT NULL
    )""",
]


def _alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return cfg


def test_0009_upgrade_creates_tables_and_downgrade_removes_them_without_touching_existing_data():
    # Same isolation pattern as test_projects_migration.py: alembic/env.py
    # always resolves its own sqlalchemy.url from
    # get_settings().sync_database_url (FORGE_DATA_DIR-derived), ignoring
    # any url passed on the Config object.
    from app.core.config import get_settings

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    tmp_dir = tempfile.mkdtemp(prefix="forge-knowledge-migration-test-")
    os.environ["FORGE_DATA_DIR"] = tmp_dir
    get_settings.cache_clear()

    try:
        db_path = Path(tmp_dir) / "forge.db"
        cfg = _alembic_config()

        engine = sa.create_engine(f"sqlite:///{db_path}")
        with engine.begin() as conn:
            for ddl in _PRE_0009_DDL:
                conn.execute(sa.text(ddl))
            conn.execute(
                sa.text(
                    "INSERT INTO notes (id, title, content, color, pos_x, pos_y, width, height, z_index, "
                    "pinned, archived, created_at, updated_at) "
                    "VALUES ('n1','pre-existing note','C','#fff',0,0,280,220,0,0,0,'2026-01-01','2026-01-01')"
                )
            )
            conn.execute(sa.text("INSERT INTO tags (id, name, color) VALUES ('t1','client-a','#000')"))
        engine.dispose()
        command.stamp(cfg, "0008")

        command.upgrade(cfg, "head")

        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        tables = inspector.get_table_names()
        assert "note_tag_links" in tables
        assert "document_tag_links" in tables
        assert "knowledge_links" in tables
        link_columns = {c["name"] for c in inspector.get_columns("knowledge_links")}
        assert link_columns == {"id", "source_type", "source_id", "target_type", "target_id", "created_at"}

        with engine.connect() as conn:
            title = conn.execute(sa.text("SELECT title FROM notes WHERE id='n1'")).scalar_one()
            assert title == "pre-existing note"
            tag = conn.execute(sa.text("SELECT name FROM tags WHERE id='t1'")).scalar_one()
            assert tag == "client-a"
        engine.dispose()

        command.downgrade(cfg, "0008")

        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        tables = inspector.get_table_names()
        assert "knowledge_links" not in tables
        assert "note_tag_links" not in tables
        assert "document_tag_links" not in tables
        with engine.connect() as conn:
            title = conn.execute(sa.text("SELECT title FROM notes WHERE id='n1'")).scalar_one()
            assert title == "pre-existing note"
        engine.dispose()

        command.upgrade(cfg, "head")
        engine = sa.create_engine(f"sqlite:///{db_path}")
        inspector = sa.inspect(engine)
        assert "knowledge_links" in inspector.get_table_names()
        with engine.connect() as conn:
            title = conn.execute(sa.text("SELECT title FROM notes WHERE id='n1'")).scalar_one()
            assert title == "pre-existing note"
        engine.dispose()
    finally:
        if previous_data_dir is None:
            os.environ.pop("FORGE_DATA_DIR", None)
        else:
            os.environ["FORGE_DATA_DIR"] = previous_data_dir
        get_settings.cache_clear()
