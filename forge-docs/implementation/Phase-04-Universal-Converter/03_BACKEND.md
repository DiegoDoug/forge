# Universal Converter — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — filled in against [`01_SPEC.md`](01_SPEC.md) v0.2.0, pending owner review.
> **Last Updated:** 2026-07-23

---

## 1. Service boundary

**Extends existing subpackages; does not create a new top-level `services/converter/` package.** This follows [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §3's explicit guidance to prefer extending for consolidation phases like this one.

- `backend/app/services/converters/` (today: only `cron.py`) gains a new `providers/` submodule — this is where the provider interface and registry live.
- `backend/app/services/ingest/` (today: `converter.py`, `formats.py`, `jobs.py`, `postprocess.py`, `vision.py`) is **not modified**. It is wrapped, not rewritten.

```
backend/app/services/converters/
├── cron.py                  # unchanged
├── providers/
│   ├── __init__.py           # ConverterProvider protocol + registry
│   └── markitdown.py         # thin adapter registering services/ingest's pipeline as a provider
```

### Why a wrapper instead of moving `services/ingest/` code into `services/converters/`

Moving five modules (job store, worker pool, vision assist, postprocessing) into a new location touches every import site for zero behavioral benefit and directly risks the "no breaking changes, preserve every existing feature" constraint on a pipeline that already works. A thin adapter (~30–50 lines) that imports `services.ingest.converter`, `services.ingest.formats`, and `services.ingest.jobs` as-is and exposes them through the `ConverterProvider` shape gets the architectural benefit (a real, registrable interface) at a fraction of the risk. If a later phase decides the `ingest` name itself should retire in favor of `converters` terminology throughout, that is a separate, explicitly-scoped rename (candidate for its own ADR, following the [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md) aliasing precedent) — not something this phase does opportunistically while also introducing the provider abstraction.

## 2. The `ConverterProvider` interface

```python
# backend/app/services/converters/providers/__init__.py
from typing import Protocol

class ConverterProvider(Protocol):
    slug: str                       # e.g. "markitdown"
    label: str                      # e.g. "Documents → Markdown"
    input_extensions: frozenset[str]  # e.g. formats.KNOWN_EXTENSIONS
    output_format: str               # e.g. "markdown"

    def submit(self, job: "Job") -> None:
        """Queue every pending file task in `job` for conversion."""

_PROVIDERS: list[ConverterProvider] = []

def register(provider: ConverterProvider) -> None:
    _PROVIDERS.append(provider)

def list_providers() -> list[ConverterProvider]:
    return list(_PROVIDERS)
```

```python
# backend/app/services/converters/providers/markitdown.py
from app.services.ingest import converter, formats

class MarkItDownProvider:
    slug = "markitdown"
    label = "Documents → Markdown"
    input_extensions = formats.KNOWN_EXTENSIONS
    output_format = "markdown"

    def submit(self, job) -> None:
        converter.submit(job)  # delegates entirely to the existing, unmodified pipeline

register(MarkItDownProvider())
```

This is intentionally minimal — a `Protocol` (structural typing, no inheritance required), a module-level list as the registry (no database, no dynamic plugin loading), and one concrete provider that is a pass-through to code that already works. **Cron is deliberately not forced into this interface**: it's a text-in/text-out computation (expression → description + next-run times), not a file conversion, and shoehorning it into a `ConverterProvider` shape designed around file extensions and job submission would be abstraction for its own sake — per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md), no premature generalization beyond what the actual shipped capabilities need. It stays exactly as it is: `services/converters/cron.py` plus its existing route.

### Trade-off: why introduce this interface at all, if no new provider ships this phase?

The counter-argument — "you're speccing scaffolding for a feature (a second provider) that doesn't exist yet" — is real and worth stating plainly rather than glossing over. The justification: `01_SPEC.md`'s scope decision explicitly separates "no new conversion direction this phase" from "no future extensibility work this phase" — the roadmap and the phase's own Engineering Principles call for "favor modularity and future extensibility over one-off implementations," and the concrete, near-term motivating case is real: Phase 08 (Developer Toolkit) or a Universal Converter fast-follow adding, say, a server-side "PDF → DOCX" or "JSON ⇄ YAML" provider should be able to do so by adding one adapter module and one `register()` call — not by re-deriving "how does the unified page discover what it can convert" from scratch. The interface is ~40 lines total and wraps code that already exists; it is not a speculative framework, it is the smallest abstraction that makes "one more provider" a additive change instead of a page rewrite. If the project owner judges even this is premature, the fallback is requirement 6–7 in `01_SPEC.md` become no-ops and the phase ships as a pure UI/nav consolidation — flagging this trade-off explicitly for review rather than deciding it unilaterally.

## 3. Integration with existing services

- `services/converters/providers/markitdown.py` imports from `services/ingest/` (`converter.submit`, `formats.KNOWN_EXTENSIONS`) — a same-layer, backend `services/`-to-`services/` call, which is the established pattern already used by `api/routes/ingest.py` calling `services/notes/service.py` for the save-to-notes bridge. This is not a "features import from each other" violation — that hard rule (per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1) governs the *frontend* `features/` folders; backend `services/` modules already call into each other where one capability's output feeds another (Ingest → Notes today; Converters-provider → Ingest's pipeline in this phase).
- No change to `services/notes/`, `services/documents/`, `services/activity/`, or any other existing service.

## 4. Architectural compliance

- [x] Routers stay thin — the new `/api/converters/providers` route (see [`06_API.md`](06_API.md)) is a one-line call to `providers.list_providers()`; all decision-making stays in `services/`.
- [x] No cross-feature imports introduced at the frontend level (the change described here is entirely backend `services/`-layer).
- [x] No new external dependency — `typing.Protocol` is stdlib; nothing added to [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md).
- [x] Existing `/api/ingest/*` routes and `/api/converters/cron/parse` are not modified — see [`06_API.md`](06_API.md) for the full backward-compatibility accounting.

## 5. Performance considerations

No new performance surface: the provider registry is a Python list populated once at import time (`register()` calls at module load), looked up in O(n) where n is currently 1 — negligible. The actual conversion work (MarkItDown, vision LLM, worker pool sizing via `ingest_workers`) is unchanged, since `MarkItDownProvider.submit()` delegates directly to the existing `converter.submit()` without any added indirection in the hot path (per-file conversion still runs on the same `ThreadPoolExecutor`).

## 6. Error handling

Unchanged. `AppError` / `NotFoundError` conventions and the global exception handler (`app/core/errors.py`) are not touched by this phase. The new `/api/converters/providers` endpoint has no failure modes beyond the standard auth-required 401 (no request body, no I/O beyond an in-memory list read).

## 7. TODO

- [ ] Project-owner review of the `ConverterProvider` interface and the trade-off discussion in §2, in particular whether the abstraction is worth introducing with only one provider registered.
- [ ] This document, along with [`01_SPEC.md`](01_SPEC.md), [`02_UI.md`](02_UI.md), [`04_DATABASE.md`](04_DATABASE.md), and [`06_API.md`](06_API.md), must be reviewed before Stage 4 (implementation task breakdown) begins.

## 8. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
