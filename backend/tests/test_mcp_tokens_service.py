from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.models import *  # noqa: F401,F403 (register every table on SQLModel.metadata)
from app.models.base import utcnow
from app.services.mcp import tokens as tokens_service


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


async def test_issue_returns_a_row_and_a_raw_token_never_matching_the_stored_hash(db_session):
    token, raw = await tokens_service.issue(db_session, name="Claude Code", scopes=["forge:read", "forge:write"])

    assert token.name == "Claude Code"
    assert token.token_hash != raw, "the raw token must never be stored verbatim"
    assert raw not in token.token_hash
    assert token.revoked_at is None
    assert token.last_used_at is None


async def test_verify_succeeds_for_a_freshly_issued_token(db_session):
    _, raw = await tokens_service.issue(db_session, name="t", scopes=["forge:read"])

    ctx = await tokens_service.verify(db_session, raw)

    assert ctx is not None
    assert ctx.scopes == frozenset({"forge:read"})
    assert ctx.has_scope("forge:read")
    assert not ctx.has_scope("forge:write")


async def test_verify_fails_for_a_garbage_token(db_session):
    await tokens_service.issue(db_session, name="t", scopes=["forge:read"])

    assert await tokens_service.verify(db_session, "not-a-real-token") is None


async def test_verify_fails_after_revocation_immediately(db_session):
    token, raw = await tokens_service.issue(db_session, name="t", scopes=["forge:read"])
    assert await tokens_service.verify(db_session, raw) is not None

    revoked = await tokens_service.revoke(db_session, token.id)

    assert revoked is not None
    assert revoked.revoked_at is not None
    assert await tokens_service.verify(db_session, raw) is None


async def test_revoke_is_idempotent_and_returns_none_for_an_unknown_id(db_session):
    token, _ = await tokens_service.issue(db_session, name="t", scopes=[])

    first = await tokens_service.revoke(db_session, token.id)
    second = await tokens_service.revoke(db_session, token.id)

    assert first.revoked_at == second.revoked_at
    assert await tokens_service.revoke(db_session, "does-not-exist") is None


async def test_list_tokens_orders_newest_first(db_session):
    await tokens_service.issue(db_session, name="first", scopes=[])
    await asyncio.sleep(0.01)
    await tokens_service.issue(db_session, name="second", scopes=[])

    tokens = await tokens_service.list_tokens(db_session)

    assert [t.name for t in tokens] == ["second", "first"]


async def test_touch_last_used_sets_the_field_on_first_call(db_session):
    token, _ = await tokens_service.issue(db_session, name="t", scopes=[])
    assert token.last_used_at is None

    await tokens_service.touch_last_used(db_session, token.id)

    refreshed = await tokens_service.list_tokens(db_session)
    assert refreshed[0].last_used_at is not None


async def test_touch_last_used_is_throttled_within_the_five_minute_window(db_session, monkeypatch):
    token, _ = await tokens_service.issue(db_session, name="t", scopes=[])
    await tokens_service.touch_last_used(db_session, token.id)
    first_value = (await tokens_service.list_tokens(db_session))[0].last_used_at

    # Second call moments later must NOT move last_used_at - proves the
    # write is throttled, not merely "eventually correct" (AC4a).
    await tokens_service.touch_last_used(db_session, token.id)
    second_value = (await tokens_service.list_tokens(db_session))[0].last_used_at

    assert second_value == first_value


async def test_touch_last_used_updates_again_once_the_throttle_window_has_passed(db_session):
    token, _ = await tokens_service.issue(db_session, name="t", scopes=[])
    await tokens_service.touch_last_used(db_session, token.id)
    stale_time = utcnow() - timedelta(minutes=10)

    # Directly backdate the stored value to simulate the throttle window
    # having elapsed, without sleeping 5 real minutes in a test.
    from sqlmodel import select

    from app.models.mcp_token import McpToken

    result = await db_session.execute(select(McpToken).where(McpToken.id == token.id))
    row = result.scalar_one()
    row.last_used_at = stale_time
    db_session.add(row)
    await db_session.commit()

    await tokens_service.touch_last_used(db_session, token.id)

    refreshed = (await tokens_service.list_tokens(db_session))[0]
    assert refreshed.last_used_at > stale_time


async def test_touch_last_used_is_a_safe_no_op_for_an_unknown_token_id(db_session):
    await tokens_service.touch_last_used(db_session, "does-not-exist")  # must not raise
