"""The `ConverterProvider` interface and registry.

Introduced in Universal Converter (Phase 04) Milestone 2 as pure, additive
scaffolding — per `03_BACKEND.md` §2's trade-off discussion, this module is
deliberately proven only against a throwaway fake provider in this milestone.
Wiring a real provider (the existing MarkItDown/Ingest pipeline) is
Milestone 3's job, not this one's, per `09_IMPLEMENTATION_TASKS.md` §0.1's
architecture-only classification for this milestone.

`submit`'s `job` parameter is intentionally left untyped here rather than
importing a concrete `Job` class — this module has zero dependency on
`services.ingest` (or any other service) by design. The concrete shape of
`job` is defined by whatever pipeline a given provider wraps.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ConverterProvider(Protocol):
    slug: str
    label: str
    input_extensions: frozenset[str]
    output_format: str

    def submit(self, job) -> None:
        """Queue every pending file task in `job` for conversion."""
        ...


_PROVIDERS: list[ConverterProvider] = []


def register(provider: ConverterProvider) -> None:
    _PROVIDERS.append(provider)


def list_providers() -> list[ConverterProvider]:
    return list(_PROVIDERS)
