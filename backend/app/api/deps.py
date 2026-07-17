from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError, UnauthorizedError
from app.core.security import verify_session_token
from app.database.session import get_session
from app.services.settings import service as settings_service

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class SetupRequiredError(AppError):
    def __init__(self) -> None:
        super().__init__("Complete first-run setup before continuing", status_code=401, code="setup_required")


async def require_auth(
    session: SessionDep,
    forge_session: Annotated[str | None, Cookie()] = None,
) -> None:
    config = await settings_service.get_config(session)
    if config.master_password_hash is None:
        raise SetupRequiredError()
    if not forge_session or not verify_session_token(forge_session, config.master_password_hash):
        raise UnauthorizedError("Session expired or invalid, please unlock Forge again")


AuthDep = Depends(require_auth)


def session_cookie_kwargs() -> dict:
    settings = get_settings()
    return {
        "key": settings.session_cookie_name,
        "httponly": True,
        "samesite": "lax",
        "secure": settings.session_cookie_secure,
        "max_age": settings.session_ttl_minutes * 60,
        "path": "/",
    }
