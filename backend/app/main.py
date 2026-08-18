from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.version import VERSION
from app.mcp.server import mount_mcp_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _run_migrations() -> None:
    settings = get_settings()
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.ingest_jobs_dir.mkdir(parents=True, exist_ok=True)
    _run_migrations()

    from app.services.ingest.jobs import store as ingest_job_store

    ingest_job_store.start_cleanup_thread()

    # The MCP app (if mounted - see create_app()) is a nested ASGI app with
    # its own lifespan (it starts/stops the Streamable HTTP session manager).
    # Starlette does not automatically forward lifespan events to a mounted
    # sub-app, so it must be chained explicitly here or every /mcp request
    # would hang waiting on a session manager that never started. See
    # app/mcp/server.py::build_mcp_asgi_app.
    mcp_raw_app = getattr(app.state, "mcp_raw_app", None)
    if mcp_raw_app is not None:
        async with mcp_raw_app.router.lifespan_context(mcp_raw_app):
            yield
    else:
        yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Forge API", version=VERSION, lifespan=lifespan)

    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(api_router)

    # Only mounts /mcp (and returns a non-None raw app for the lifespan
    # above to chain) when FORGE_MCP_ENABLED is true - disabled instances
    # get no new attack surface (01_SPEC.md SS3).
    app.state.mcp_raw_app = mount_mcp_app(app)
    return app


app = create_app()
