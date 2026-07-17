from __future__ import annotations

from fastapi import APIRouter, Response

from app.api.deps import AuthDep, SessionDep, session_cookie_kwargs
from app.core.config import get_settings
from app.core.security import issue_session_token
from app.schemas.auth import ChangePasswordIn, MasterPasswordIn, SessionOut, SetupStatusOut
from app.services.settings import service as settings_service

router = APIRouter(tags=["auth"])


@router.get("/setup/status", response_model=SetupStatusOut)
async def setup_status(session: SessionDep) -> SetupStatusOut:
    return SetupStatusOut(setup_completed=await settings_service.is_setup_complete(session))


@router.post("/setup", response_model=SessionOut)
async def setup(body: MasterPasswordIn, session: SessionDep, response: Response) -> SessionOut:
    config = await settings_service.complete_setup(session, body.master_password)
    _set_session_cookie(response, config.master_password_hash)
    return SessionOut(authenticated=True)


@router.post("/auth/unlock", response_model=SessionOut)
async def unlock(body: MasterPasswordIn, session: SessionDep, response: Response) -> SessionOut:
    config = await settings_service.verify_unlock(session, body.master_password)
    _set_session_cookie(response, config.master_password_hash)
    return SessionOut(authenticated=True)


@router.post("/auth/lock", response_model=SessionOut, dependencies=[AuthDep])
async def lock(response: Response) -> SessionOut:
    response.delete_cookie(get_settings().session_cookie_name, path="/")
    return SessionOut(authenticated=False)


@router.get("/auth/session", response_model=SessionOut, dependencies=[AuthDep])
async def check_session() -> SessionOut:
    return SessionOut(authenticated=True)


@router.put("/auth/password", response_model=SessionOut, dependencies=[AuthDep])
async def change_password(body: ChangePasswordIn, session: SessionDep, response: Response) -> SessionOut:
    config = await settings_service.change_master_password(session, body.current_password, body.new_password)
    _set_session_cookie(response, config.master_password_hash)
    return SessionOut(authenticated=True)


def _set_session_cookie(response: Response, password_hash: str) -> None:
    settings = get_settings()
    token = issue_session_token(password_hash, settings.session_ttl_minutes)
    response.set_cookie(value=token, **session_cookie_kwargs())
