from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.errors import NotFoundError
from app.core.security import get_vault_crypto
from app.models.activity import ActivityAction
from app.models.base import utcnow
from app.models.model_playground import ProviderCredential
from app.services import activity
from app.services.model_playground.providers import PROVIDER_REGISTRY


async def list_credentials(session: AsyncSession) -> list[ProviderCredential]:
    result = await session.execute(select(ProviderCredential).order_by(ProviderCredential.provider))
    return list(result.scalars().all())


async def list_provider_availability(session: AsyncSession) -> list[dict]:
    configured = {c.provider for c in await list_credentials(session)}
    return [
        {
            "provider": spec.key,
            "display_name": spec.display_name,
            "configured": spec.key in configured,
            "models": list(spec.models),
        }
        for spec in PROVIDER_REGISTRY.values()
    ]


async def _get_credential(session: AsyncSession, provider: str) -> ProviderCredential | None:
    result = await session.execute(select(ProviderCredential).where(ProviderCredential.provider == provider))
    return result.scalar_one_or_none()


async def create_or_replace_credential(
    session: AsyncSession, *, provider: str, label: str | None, api_key: str
) -> ProviderCredential:
    crypto = get_vault_crypto()
    encrypted = crypto.encrypt_str(api_key)
    display_name = PROVIDER_REGISTRY[provider].display_name
    resolved_label = label or display_name

    existing = await _get_credential(session, provider)
    if existing is not None:
        existing.label = resolved_label
        existing.encrypted_api_key = encrypted
        existing.updated_at = utcnow()
        session.add(existing)
        activity.record(session, ActivityAction.updated, "provider_credential", existing.id, f'Replaced key for "{display_name}"')
        await session.commit()
        await session.refresh(existing)
        return existing

    credential = ProviderCredential(provider=provider, label=resolved_label, encrypted_api_key=encrypted)
    session.add(credential)
    await session.flush()
    activity.record(session, ActivityAction.created, "provider_credential", credential.id, f'Configured "{display_name}"')
    await session.commit()
    await session.refresh(credential)
    return credential


async def delete_credential(session: AsyncSession, credential_id: str) -> None:
    result = await session.execute(select(ProviderCredential).where(ProviderCredential.id == credential_id))
    credential = result.scalar_one_or_none()
    if credential is None:
        raise NotFoundError("Provider credential not found")
    label = credential.label
    await session.delete(credential)
    activity.record(session, ActivityAction.deleted, "provider_credential", credential_id, f'Removed key for "{label}"')
    await session.commit()


async def decrypt_api_key(credential: ProviderCredential) -> str:
    return get_vault_crypto().decrypt_str(credential.encrypted_api_key)
