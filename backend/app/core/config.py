"""Application configuration.

All settings are read from environment variables (or an .env file in
development). Docker Secrets are supported for anything security-sensitive
via the `*_FILE` convention: if `FORGE_MASTER_KEY_FILE` is set, its file
contents win over `FORGE_MASTER_KEY`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _read_secret_file(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8").strip()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FORGE_", env_file=".env", extra="ignore")

    app_name: str = "Forge"
    environment: str = "production"
    data_dir: Path = Path("/data")

    # Comma-separated list of origins allowed to call the API in dev (e.g. the
    # Next.js dev server). In production the frontend and API are served
    # same-origin behind the bundled reverse proxy, so this is normally empty.
    cors_origins: str = ""

    # Root symmetric key used to encrypt vault secrets at rest and to sign
    # session cookies. Any non-empty string works (it is stretched via BLAKE2b
    # into a 32-byte key) but a high-entropy random value is strongly
    # recommended: `openssl rand -base64 32`.
    master_key: str | None = None
    master_key_file: str | None = None

    session_cookie_name: str = "forge_session"
    session_ttl_minutes: int = 60 * 12
    # Off by default: Forge is commonly self-hosted over plain HTTP on a LAN,
    # and a `Secure` cookie is silently dropped by browsers on non-HTTPS
    # origins, which would otherwise brick login. Set to true once Forge sits
    # behind TLS (a reverse proxy, Tailscale, etc).
    session_cookie_secure: bool = False

    max_upload_file_size_mb: int = 200
    max_upload_batch_files: int = 50
    ingest_job_ttl_minutes: int = 120
    ingest_workers: int = 2

    vision_enabled: bool = False
    vision_api_key: str | None = None
    vision_base_url: str | None = None
    vision_model: str = "gpt-4o-mini"
    vision_pdf_mode: str = "auto"
    vision_pdf_char_threshold: int = 40
    vision_pdf_max_pages: int = 30
    vision_pdf_dpi: int = 150
    vision_max_concurrency: int = 4

    @property
    def resolved_master_key(self) -> str:
        secret = _read_secret_file(self.master_key_file) or self.master_key
        if not secret:
            raise RuntimeError(
                "FORGE_MASTER_KEY (or FORGE_MASTER_KEY_FILE) is not set. "
                "Generate one with `openssl rand -base64 32` and set it as an "
                "environment variable or Docker secret before starting Forge."
            )
        return secret

    @property
    def database_path(self) -> Path:
        return self.data_dir / "forge.db"

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database_path}"

    @property
    def sync_database_url(self) -> str:
        """Plain (non-async) URL used only by Alembic migrations, which run
        synchronously to avoid nesting an event loop inside uvicorn's
        already-running one during app startup."""
        return f"sqlite:///{self.database_path}"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def ingest_jobs_dir(self) -> Path:
        return self.data_dir / "ingest-jobs"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
