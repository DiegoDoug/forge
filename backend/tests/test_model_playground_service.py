from __future__ import annotations

import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select

from app.core.errors import AppError, NotFoundError
from app.core.security import get_vault_crypto
from app.models import *  # noqa: F401,F403 (register every table on SQLModel.metadata)
from app.models.activity import ActivityLog
from app.models.model_playground import ProviderCredential
from app.services.model_playground import credentials as credentials_service
from app.services.model_playground import runs as runs_service
from app.services.model_playground.providers import PROVIDER_REGISTRY
from app.services.model_playground.providers.base import AdapterResult
from app.services.model_playground.runs import RunTarget


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


class _FakeAdapter:
    def __init__(self, *, text="hello", delay=0.0, error=None, prompt_tokens=10, completion_tokens=5):
        self.text = text
        self.delay = delay
        self.error = error
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.calls: list[dict] = []

    async def complete(
        self, *, api_key: str, model: str, prompt: str, base_url: str | None = None
    ) -> AdapterResult:
        self.calls.append({"api_key": api_key, "model": model, "prompt": prompt, "base_url": base_url})
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return AdapterResult(
            response_text=self.text, prompt_tokens=self.prompt_tokens, completion_tokens=self.completion_tokens
        )


@pytest.fixture(autouse=True)
def _restore_adapters():
    originals = {key: spec.adapter for key, spec in PROVIDER_REGISTRY.items()}
    yield
    for key, adapter in originals.items():
        object.__setattr__(PROVIDER_REGISTRY[key], "adapter", adapter)


def _install_fake_adapter(provider: str, adapter: _FakeAdapter) -> None:
    object.__setattr__(PROVIDER_REGISTRY[provider], "adapter", adapter)


# --- Credentials -----------------------------------------------------------


async def test_create_credential_stores_ciphertext_not_plaintext(db_session):
    credential = await credentials_service.create_or_replace_credential(
        db_session, provider="openai", label="My key", api_key="sk-super-secret"
    )

    assert b"sk-super-secret" not in credential.encrypted_api_key
    decrypted = await credentials_service.decrypt_api_key(credential)
    assert decrypted == "sk-super-secret"


async def test_create_credential_round_trips_via_vault_crypto_directly(db_session):
    credential = await credentials_service.create_or_replace_credential(
        db_session, provider="anthropic", label=None, api_key="anthropic-key"
    )

    assert get_vault_crypto().decrypt_str(credential.encrypted_api_key) == "anthropic-key"
    assert credential.label == "Anthropic"  # defaults to display name


async def test_creating_second_credential_for_same_provider_replaces_not_duplicates(db_session):
    first = await credentials_service.create_or_replace_credential(
        db_session, provider="openai", label="First", api_key="key-1"
    )
    second = await credentials_service.create_or_replace_credential(
        db_session, provider="openai", label="Second", api_key="key-2"
    )

    assert first.id == second.id
    result = await db_session.execute(select(ProviderCredential).where(ProviderCredential.provider == "openai"))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert await credentials_service.decrypt_api_key(rows[0]) == "key-2"


async def test_provider_availability_reflects_configured_state(db_session):
    availability = await credentials_service.list_provider_availability(db_session)
    by_provider = {a["provider"]: a for a in availability}
    assert by_provider["openai"]["configured"] is False
    assert by_provider["anthropic"]["configured"] is False

    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k")

    availability = await credentials_service.list_provider_availability(db_session)
    by_provider = {a["provider"]: a for a in availability}
    assert by_provider["openai"]["configured"] is True
    assert by_provider["anthropic"]["configured"] is False
    assert by_provider["openai"]["models"] == list(PROVIDER_REGISTRY["openai"].models)


async def test_delete_missing_credential_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await credentials_service.delete_credential(db_session, "does-not-exist")


async def test_delete_credential_writes_activity_log_without_the_key(db_session):
    credential = await credentials_service.create_or_replace_credential(
        db_session, provider="openai", label="Prod key", api_key="sk-should-not-appear"
    )

    await credentials_service.delete_credential(db_session, credential.id)

    result = await db_session.execute(select(ActivityLog).where(ActivityLog.action == "deleted"))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert "sk-should-not-appear" not in rows[0].summary
    assert "Prod key" in rows[0].summary


# --- Runs --------------------------------------------------------------


async def test_create_run_rejects_target_with_no_configured_credential(db_session):
    with pytest.raises(AppError):
        await runs_service.create_run(
            db_session, prompt="hi", targets=[RunTarget(provider="openai", model="gpt-4.1")]
        )


async def test_create_run_all_targets_succeed_independently(db_session):
    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k1")
    await credentials_service.create_or_replace_credential(db_session, provider="anthropic", label=None, api_key="k2")
    _install_fake_adapter("openai", _FakeAdapter(text="openai says hi"))
    _install_fake_adapter("anthropic", _FakeAdapter(text="anthropic says hi"))

    run = await runs_service.create_run(
        db_session,
        prompt="hi",
        targets=[
            RunTarget(provider="openai", model="gpt-4.1"),
            RunTarget(provider="anthropic", model="claude-sonnet-5"),
        ],
    )

    assert run.prompt == "hi"
    assert len(run.results) == 2
    assert all(r.status == "success" for r in run.results)
    texts = {r.provider: r.response_text for r in run.results}
    assert texts["openai"] == "openai says hi"
    assert texts["anthropic"] == "anthropic says hi"


async def test_create_run_one_target_failing_does_not_affect_the_other(db_session):
    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k1")
    await credentials_service.create_or_replace_credential(db_session, provider="anthropic", label=None, api_key="k2")
    _install_fake_adapter("openai", _FakeAdapter(error=RuntimeError("boom")))
    _install_fake_adapter("anthropic", _FakeAdapter(text="still works"))

    run = await runs_service.create_run(
        db_session,
        prompt="hi",
        targets=[
            RunTarget(provider="openai", model="gpt-4.1"),
            RunTarget(provider="anthropic", model="claude-sonnet-5"),
        ],
    )

    by_provider = {r.provider: r for r in run.results}
    assert by_provider["openai"].status == "error"
    assert by_provider["openai"].error_message  # user-legible, non-empty
    assert "boom" not in by_provider["openai"].error_message  # never the raw exception text
    assert by_provider["anthropic"].status == "success"
    assert by_provider["anthropic"].response_text == "still works"


async def test_create_run_timeout_is_isolated_to_that_target(db_session, monkeypatch):
    monkeypatch.setattr(runs_service, "TIMEOUT_SECONDS", 0.05)
    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k1")
    await credentials_service.create_or_replace_credential(db_session, provider="anthropic", label=None, api_key="k2")
    _install_fake_adapter("openai", _FakeAdapter(delay=1.0))
    _install_fake_adapter("anthropic", _FakeAdapter(text="fast"))

    run = await runs_service.create_run(
        db_session,
        prompt="hi",
        targets=[
            RunTarget(provider="openai", model="gpt-4.1"),
            RunTarget(provider="anthropic", model="claude-sonnet-5"),
        ],
    )

    by_provider = {r.provider: r for r in run.results}
    assert by_provider["openai"].status == "timeout"
    assert by_provider["anthropic"].status == "success"


async def test_deleting_credential_does_not_corrupt_past_run_results(db_session):
    credential = await credentials_service.create_or_replace_credential(
        db_session, provider="openai", label=None, api_key="k1"
    )
    _install_fake_adapter("openai", _FakeAdapter(text="preserved"))
    run = await runs_service.create_run(db_session, prompt="hi", targets=[RunTarget(provider="openai", model="gpt-4.1")])

    await credentials_service.delete_credential(db_session, credential.id)

    reloaded = await runs_service.get_run(db_session, run.id)
    assert len(reloaded.results) == 1
    assert reloaded.results[0].status == "success"
    assert reloaded.results[0].response_text == "preserved"


async def test_delete_run_cascades_to_results(db_session):
    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k1")
    _install_fake_adapter("openai", _FakeAdapter(text="x"))
    run = await runs_service.create_run(db_session, prompt="hi", targets=[RunTarget(provider="openai", model="gpt-4.1")])

    await runs_service.delete_run(db_session, run.id)

    with pytest.raises(NotFoundError):
        await runs_service.get_run(db_session, run.id)


async def test_delete_missing_run_raises_not_found(db_session):
    with pytest.raises(NotFoundError):
        await runs_service.delete_run(db_session, "does-not-exist")


async def test_list_runs_orders_most_recent_first(db_session):
    await credentials_service.create_or_replace_credential(db_session, provider="openai", label=None, api_key="k1")
    _install_fake_adapter("openai", _FakeAdapter(text="x"))
    first = await runs_service.create_run(db_session, prompt="first", targets=[RunTarget(provider="openai", model="gpt-4.1")])
    second = await runs_service.create_run(db_session, prompt="second", targets=[RunTarget(provider="openai", model="gpt-4.1")])

    runs = await runs_service.list_runs(db_session)

    assert [r.id for r in runs] == [second.id, first.id]


# --- Provider registry (ADR-0013) -------------------------------------------


def test_provider_registry_includes_v1_and_extended_providers():
    assert set(PROVIDER_REGISTRY) == {"openai", "anthropic", "deepseek", "kimi", "glm", "gemini", "custom"}


def test_only_custom_provider_requires_base_url_or_allows_custom_model():
    for key, spec in PROVIDER_REGISTRY.items():
        if key == "custom":
            assert spec.requires_base_url is True
            assert spec.allows_custom_model is True
            assert spec.models == ()
        else:
            assert spec.requires_base_url is False
            assert spec.allows_custom_model is False
            assert len(spec.models) > 0


def test_unknown_provider_key_is_not_in_registry():
    assert "made-up" not in PROVIDER_REGISTRY


# --- base_url on ProviderCredential (ADR-0013) ------------------------------


async def test_create_credential_for_custom_provider_stores_base_url(db_session):
    credential = await credentials_service.create_or_replace_credential(
        db_session, provider="custom", label="My Endpoint", api_key="sk-custom", base_url="https://example.com/v1"
    )

    assert credential.base_url == "https://example.com/v1"
    assert await credentials_service.decrypt_api_key(credential) == "sk-custom"


async def test_create_credential_for_named_provider_has_no_base_url_by_default(db_session):
    credential = await credentials_service.create_or_replace_credential(
        db_session, provider="deepseek", label=None, api_key="sk-deepseek"
    )

    assert credential.base_url is None


async def test_provider_availability_reflects_new_provider_flags(db_session):
    availability = await credentials_service.list_provider_availability(db_session)
    by_provider = {a["provider"]: a for a in availability}

    assert by_provider["custom"]["requires_base_url"] is True
    assert by_provider["custom"]["allows_custom_model"] is True
    assert by_provider["custom"]["models"] == []
    assert by_provider["deepseek"]["requires_base_url"] is False
    assert by_provider["deepseek"]["models"] == list(PROVIDER_REGISTRY["deepseek"].models)


# --- Adapter routing (ADR-0013) ---------------------------------------------


async def test_deepseek_kimi_glm_gemini_route_through_openai_compatible_adapter_with_fixed_base_url():
    from app.services.model_playground.providers.openai_compatible_adapter import OpenAICompatibleAdapter

    expected = {
        "deepseek": "https://api.deepseek.com/v1",
        "kimi": "https://api.moonshot.cn/v1",
        "glm": "https://open.bigmodel.cn/api/paas/v4",
        "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    }
    for key, base_url in expected.items():
        adapter = PROVIDER_REGISTRY[key].adapter
        assert isinstance(adapter, OpenAICompatibleAdapter)
        assert adapter.default_base_url == base_url


async def test_custom_provider_adapter_has_no_fixed_default_base_url():
    from app.services.model_playground.providers.openai_compatible_adapter import OpenAICompatibleAdapter

    adapter = PROVIDER_REGISTRY["custom"].adapter
    assert isinstance(adapter, OpenAICompatibleAdapter)
    assert adapter.default_base_url is None


async def test_openai_compatible_adapter_calls_openai_sdk_with_resolved_base_url(monkeypatch):
    from app.services.model_playground.providers.openai_compatible_adapter import OpenAICompatibleAdapter

    captured: dict = {}

    class _FakeMessage:
        content = "hello from fake"

    class _FakeChoice:
        message = _FakeMessage()

    class _FakeUsage:
        prompt_tokens = 4
        completion_tokens = 6

    class _FakeResponse:
        choices = [_FakeChoice()]
        usage = _FakeUsage()

    class _FakeCompletions:
        async def create(self, **kwargs):
            captured["create_kwargs"] = kwargs
            return _FakeResponse()

    class _FakeChat:
        def __init__(self):
            self.completions = _FakeCompletions()

    class _FakeAsyncOpenAI:
        def __init__(self, *, api_key, base_url=None):
            captured["api_key"] = api_key
            captured["base_url"] = base_url
            self.chat = _FakeChat()

    monkeypatch.setattr("openai.AsyncOpenAI", _FakeAsyncOpenAI)

    adapter = OpenAICompatibleAdapter(default_base_url="https://default.example.com/v1")
    result = await adapter.complete(api_key="sk-test", model="test-model", prompt="hi")

    assert captured["api_key"] == "sk-test"
    assert captured["base_url"] == "https://default.example.com/v1"
    assert captured["create_kwargs"]["model"] == "test-model"
    assert result.response_text == "hello from fake"
    assert result.prompt_tokens == 4
    assert result.completion_tokens == 6

    # A call-time base_url (the Custom provider's stored credential) wins
    # over the adapter's own default.
    await adapter.complete(api_key="sk-test", model="test-model", prompt="hi", base_url="https://override.example.com/v1")
    assert captured["base_url"] == "https://override.example.com/v1"


# --- Runs with the new providers (ADR-0013) ---------------------------------


async def test_create_run_passes_stored_base_url_to_adapter_for_custom_provider(db_session):
    await credentials_service.create_or_replace_credential(
        db_session, provider="custom", label="My Endpoint", api_key="sk-custom", base_url="https://example.com/v1"
    )
    fake = _FakeAdapter(text="custom says hi")
    _install_fake_adapter("custom", fake)

    run = await runs_service.create_run(
        db_session, prompt="hi", targets=[RunTarget(provider="custom", model="my-self-hosted-model")]
    )

    assert run.results[0].status == "success"
    assert run.results[0].response_text == "custom says hi"
    assert fake.calls[0]["base_url"] == "https://example.com/v1"
    assert fake.calls[0]["model"] == "my-self-hosted-model"


async def test_create_run_deepseek_target_succeeds_via_fake_adapter(db_session):
    await credentials_service.create_or_replace_credential(db_session, provider="deepseek", label=None, api_key="sk-ds")
    _install_fake_adapter("deepseek", _FakeAdapter(text="deepseek says hi"))

    run = await runs_service.create_run(
        db_session, prompt="hi", targets=[RunTarget(provider="deepseek", model="deepseek-chat")]
    )

    assert run.results[0].status == "success"
    assert run.results[0].provider == "deepseek"
    assert run.results[0].response_text == "deepseek says hi"
