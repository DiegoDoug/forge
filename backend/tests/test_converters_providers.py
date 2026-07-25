"""Registry tests for the `ConverterProvider` protocol.

The first half of this file (Milestone 2) is deliberately exercised only
against a throwaway fake provider — per `09_IMPLEMENTATION_TASKS.md` §0.1,
that milestone is architecture-only and must not depend on (or be proven
against) the real Ingest pipeline. Nothing in Milestone 2's own code
(`app/services/converters/providers/__init__.py`) imports `app.services.
ingest` — that remains true regardless of this test file.

The second half (Milestone 3) extends this file with the real
`MarkItDownProvider`, per the plan in `09_IMPLEMENTATION_TASKS.md`.

Import-order note: `markitdown` is imported at module level (below), not
inside a test function. `register(MarkItDownProvider())` runs once, as a
side effect, the first time this module is ever imported in the process —
if that import happened lazily inside a test function body, it would run
*after* the `isolated_registry` autouse fixture below has already replaced
`_PROVIDERS` with a throwaway per-test list, and the real registration would
land in that throwaway list and be discarded when the fixture reverts at
teardown. Importing at module level guarantees the registration fires
during collection, against the real, persistent registry, before any test's
fixture has a chance to shadow it.
"""

from __future__ import annotations

import pytest

from app.services.converters import providers
from app.services.converters.providers import markitdown


@pytest.fixture(autouse=True)
def isolated_registry(monkeypatch):
    """Every test gets its own empty registry list — `_PROVIDERS` is
    module-level, mutable, shared state, and different tests (or a future
    test module, once Milestone 3 registers a real provider at import time)
    must not see each other's registrations."""
    monkeypatch.setattr(providers, "_PROVIDERS", [])


class _FakeProvider:
    """A minimal stand-in satisfying the `ConverterProvider` protocol,
    with no relation to any real conversion pipeline."""

    def __init__(self, slug: str = "fake", label: str = "Fake Provider"):
        self.slug = slug
        self.label = label
        self.input_extensions = frozenset({".fake"})
        self.output_format = "fake-output"
        self.submitted_jobs = []

    def submit(self, job) -> None:
        self.submitted_jobs.append(job)


def test_list_providers_starts_empty():
    assert providers.list_providers() == []


def test_register_makes_a_provider_appear_exactly_once():
    fake = _FakeProvider()
    providers.register(fake)
    result = providers.list_providers()
    assert result == [fake]
    assert len(result) == 1


def test_register_preserves_multiple_distinct_providers():
    first = _FakeProvider(slug="fake-one")
    second = _FakeProvider(slug="fake-two")
    providers.register(first)
    providers.register(second)

    result = providers.list_providers()
    assert len(result) == 2
    assert {p.slug for p in result} == {"fake-one", "fake-two"}


def test_list_providers_returns_a_copy_not_the_live_registry():
    fake = _FakeProvider()
    providers.register(fake)

    snapshot = providers.list_providers()
    snapshot.append(_FakeProvider(slug="mutated-in-caller"))

    assert len(providers.list_providers()) == 1  # unaffected by the caller's mutation


def test_fake_provider_satisfies_the_converter_provider_protocol():
    fake = _FakeProvider()
    assert isinstance(fake, providers.ConverterProvider)


def test_registered_provider_exposes_its_declared_shape():
    fake = _FakeProvider(slug="fake", label="Fake Provider")
    providers.register(fake)

    [registered] = providers.list_providers()
    assert registered.slug == "fake"
    assert registered.label == "Fake Provider"
    assert registered.input_extensions == frozenset({".fake"})
    assert registered.output_format == "fake-output"


def test_provider_submit_is_callable_and_isolated_from_conversion_logic():
    """The registry itself never calls `submit` — only a caller does. This
    test exists to confirm that contract, not to exercise any real
    conversion (there is none at this milestone)."""
    fake = _FakeProvider()
    providers.register(fake)

    assert fake.submitted_jobs == []
    fake.submit("a-fake-job-object")
    assert fake.submitted_jobs == ["a-fake-job-object"]


# --- Milestone 3: the real MarkItDownProvider --------------------------------
#
# These two tests are exercised against the actual, real provider (not a
# fake) — deliberately, since Milestone 3's whole point is wiring the real
# Ingest pipeline in. They don't rely on `isolated_registry`'s empty-list
# reset: `MarkItDownProvider` is instantiated directly here, not fetched via
# `list_providers()`, so the autouse fixture above has no bearing on them.


def test_markitdown_provider_declares_the_correct_shape():
    from app.services.ingest import formats

    provider = markitdown.MarkItDownProvider()
    assert provider.slug == "markitdown"
    assert provider.input_extensions == formats.KNOWN_EXTENSIONS
    assert provider.output_format == "markdown"


def test_markitdown_provider_submit_delegates_without_transformation(monkeypatch):
    """Proves the "wrap, don't rewrite" design from `03_BACKEND.md` §1: the
    provider must call the real pipeline's `submit` exactly once, with the
    exact same object it was given — no copying, filtering, or altering."""
    from app.services.ingest import converter

    calls = []
    monkeypatch.setattr(converter, "submit", lambda job: calls.append(job))

    provider = markitdown.MarkItDownProvider()
    sentinel_job = object()
    provider.submit(sentinel_job)

    assert calls == [sentinel_job]
