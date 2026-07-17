from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import hash_master_password, verify_master_password
from app.models.app_config import AppConfig
from app.models.base import utcnow


async def get_config(session: AsyncSession) -> AppConfig:
    result = await session.execute(select(AppConfig).where(AppConfig.id == 1))
    config = result.scalar_one_or_none()
    if config is None:
        config = AppConfig(id=1)
        session.add(config)
        await session.commit()
        await session.refresh(config)
    return config


async def is_setup_complete(session: AsyncSession) -> bool:
    config = await get_config(session)
    return config.master_password_hash is not None


async def complete_setup(session: AsyncSession, master_password: str) -> AppConfig:
    config = await get_config(session)
    if config.master_password_hash is not None:
        raise ConflictError("Setup has already been completed")
    config.master_password_hash = hash_master_password(master_password)
    config.setup_completed_at = utcnow()
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config


async def verify_unlock(session: AsyncSession, master_password: str) -> AppConfig:
    config = await get_config(session)
    if config.master_password_hash is None or not verify_master_password(master_password, config.master_password_hash):
        raise UnauthorizedError("Incorrect master password")
    return config


async def change_master_password(session: AsyncSession, current_password: str, new_password: str) -> AppConfig:
    config = await verify_unlock(session, current_password)
    config.master_password_hash = hash_master_password(new_password)
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config


async def update_theme(session: AsyncSession, theme: str) -> AppConfig:
    config = await get_config(session)
    config.theme = theme
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config
