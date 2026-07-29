# Model Playground — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Confirmed — filled in against [ADR-0011](../../decisions/0011-model-playground-provider-credential-security.md), [ADR-0012](../../decisions/0012-model-playground-provider-sdk-selection.md).
> **Last Updated:** 2026-07-29

---


## 1. Service boundary

New `services/model_playground/` subpackage:

```
backend/app/services/model_playground/
  __init__.py
  credentials.py     # ProviderCredential CRUD (encrypt/decrypt via VaultCrypto)
  runs.py             # PlaygroundRun/PlaygroundResult orchestration
  providers/
    __init__.py
    base.py           # ProviderAdapter protocol + AdapterResult dataclass
    openai_adapter.py
    anthropic_adapter.py
```

No existing service is extended — this is a new, self-contained subpackage (per [`01_SPEC.md`](01_SPEC.md) §4).

## 2. Business logic

**`credentials.py`** (mirrors `services/secrets/service.py`'s shape, per ADR-0011):
- `list_credentials(session) -> list[ProviderCredential]` — metadata only, never decrypts.
- `list_provider_availability(session) -> list[ProviderAvailability]` — for every provider in `PROVIDER_REGISTRY` (openai, anthropic), reports `configured: bool` and its supported model list, joined against which providers have a stored credential. This is what powers `02_UI.md`'s "greyed out until configured" providers list and the runnable model list in the composer.
- `create_or_replace_credential(session, provider, label, api_key) -> ProviderCredential` — enforces one credential per provider (upsert on the unique `provider` column per `04_DATABASE.md` §1); encrypts via `get_vault_crypto()`.
- `delete_credential(session, credential_id) -> None`.
- No `reveal_credential` function exists — the key is never re-exposed once written (per spec FR3 / ADR-0011 §2.2). This is an intentional omission, not an oversight.

**`runs.py`**:
- `create_run(session, prompt, targets: list[RunTarget]) -> PlaygroundRun` — validates `targets` is non-empty and capped (see `06_API.md` §4), validates every target's provider has a configured credential (else raises a validation error before any outbound call is made — no partial-request round trip for an unconfigured provider), then:
  - Decrypts each targeted provider's credential in-memory.
  - Dispatches all targets **concurrently** (`asyncio.gather`, each call independently wrapped in its own try/except + `asyncio.wait_for` timeout) so one slow/failing provider doesn't block the others (spec FR7) and total wall-clock is bounded by the slowest single call, not the sum.
  - Persists one `PlaygroundResult` row per target — `status="success"` with `response_text`/token counts, or `status="error"`/`"timeout"` with a user-legible `error_message` (never the raw exception `str()` — map known SDK exception types to short messages, log the full exception server-side per the existing global-error-handler pattern in `app/core/errors.py`).
  - Persists the `PlaygroundRun` + its results in one commit.
- `list_runs(session, limit, offset) -> list[PlaygroundRun]` — metadata only (id, prompt excerpt, providers/models used, created_at) for the history list.
- `get_run(session, run_id) -> PlaygroundRun` — with results eager-loaded (`selectinload`, per the existing `secrets/service.py` pattern).
- `delete_run(session, run_id) -> None` — cascade-deletes results via the ORM relationship (`04_DATABASE.md` §2).

**`providers/base.py`**:
- `ProviderAdapter` — a small `Protocol`/ABC with one method: `async def complete(self, *, api_key: str, model: str, prompt: str) -> AdapterResult`, where `AdapterResult` carries `response_text`, `prompt_tokens: int | None`, `completion_tokens: int | None`.
- `openai_adapter.py`/`anthropic_adapter.py` implement this against the `openai`/`anthropic` SDKs respectively (per ADR-0012) — each owns its own client construction and its own provider-specific model list (`PROVIDER_REGISTRY` in `runs.py` or `providers/__init__.py` maps provider key → adapter instance + supported models).

## 3. Integration with existing services

None. The only cross-cutting dependency is `app/core/security.py::get_vault_crypto()` — a `core/` module, not another feature's internals, so this does not violate [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1's "features don't import from each other" rule (Secrets uses the same `core/` function; Model Playground doesn't import `services/secrets/*`).

## 4. Architectural compliance

- [x] Routers stay thin — `api/routes/model_playground.py` only translates HTTP ↔ Pydantic schemas ↔ `services/model_playground/*` calls; all orchestration/timeout/error-mapping logic lives in `services/`.
- [x] No cross-feature imports introduced — confirmed in §3 above.
- [x] New external dependency (`anthropic` PyPI package) recorded in [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §2/§5 (added when this dependency actually lands in `requirements.txt`, per that doc's own §4 rule).

## 5. TODO

- [ ] Assign a phase owner.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../decisions/0011-model-playground-provider-credential-security.md](../../decisions/0011-model-playground-provider-credential-security.md)
- [../../decisions/0012-model-playground-provider-sdk-selection.md](../../decisions/0012-model-playground-provider-sdk-selection.md)
