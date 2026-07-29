# Model Playground — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Confirmed — filled in against [03_BACKEND.md](03_BACKEND.md), [06_API.md](06_API.md).
> **Last Updated:** 2026-07-29

---


## 1. Backend tests

All under `backend/tests/`, following the existing `services/` unit + router integration split.

**Unit tests (`services/model_playground/`)**
- Credential round-trip: create → stored `encrypted_api_key` is not the plaintext → decrypts back to the original value via `get_vault_crypto()`.
- Credential upsert-by-provider: creating a second credential for the same `provider` replaces the first (per `04_DATABASE.md` §1's unique-on-`provider` design), not a duplicate row.
- `list_provider_availability` correctly reports `configured: false` for a provider with no credential and `true` once one exists.
- Run orchestration with **mocked provider adapters** (never real network calls in tests, per `docs/Security.md`'s degrade-gracefully principle and plain test hygiene):
  - All targets succeed → one `PlaygroundRun` with all `PlaygroundResult.status == "success"`.
  - One target's adapter raises → that result is `status == "error"` with a user-legible `error_message`, other targets are unaffected and still `"success"` (covers spec FR7 directly).
  - One target's adapter exceeds the timeout (mock a slow coroutine) → `status == "timeout"` (covers spec FR9).
  - Deleting a `ProviderCredential` after a run used it does not delete or corrupt that run's `PlaygroundResult` rows (covers spec FR4 / `04_DATABASE.md` §2's no-FK-to-credential design).
- `create_run` rejects an empty `targets` list and a `targets` list exceeding the 6-target cap (`06_API.md` §4) before dispatching any call.
- `create_run` rejects a target whose provider has no configured credential, without attempting any outbound call.

**Integration tests (router → service → test database)**
- Full CRUD lifecycle for `/api/model-playground/credentials`: create → list (no `api_key` field present in the response) → delete.
- `/api/model-playground/providers` reflects credential state accurately.
- `/api/model-playground/runs` POST with mocked adapters → 200 with mixed success/error results in one response (per `06_API.md` §3 — a partial failure is not an HTTP error).
- `/api/model-playground/runs` GET list + GET by id + DELETE.
- 404 on a missing run/credential id; 400 on empty/over-cap targets and on an unconfigured-provider target.
- Every route requires a valid session (unauthenticated request → 401), consistent with every other feature's routes.

## 2. Frontend tests

No frontend test tooling exists yet in this repo (per [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §5 — still an open TODO, unrelated to this phase). This phase does not introduce frontend test tooling on its own initiative — that's a cross-cutting tech-stack decision, not something to bootstrap inside one feature's phase. Frontend correctness for this phase is covered by §3 (manual verification) instead.

## 3. Manual verification

- Configure an OpenAI credential, confirm it appears as configured in the providers list and its models become selectable in the composer.
- Configure an Anthropic credential the same way; confirm both providers can be selected together in one run.
- Run a prompt against both providers at once; confirm both result panels populate independently (one appearing before the other is acceptable and expected).
- Temporarily use an invalid API key for one provider; confirm that panel shows a legible error while the other provider's panel still succeeds.
- Delete a credential; confirm the provider becomes unconfigured/greyed out again, and a past run that used it still opens correctly from history.
- Open history, reopen an old run, confirm prompt + results match what was originally shown.
- Delete a run from history; confirm it's gone and can't be reopened.
- Resize to a mobile viewport; confirm the composer, provider list, and result-panel grid all remain usable (per `02_UI.md` §4).
- Toggle dark mode; confirm all new surfaces render correctly (per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §1).
- Tab through the entire page (provider actions, composer checkboxes, submit, history rows) with no mouse; confirm every interactive element is reachable (per `02_UI.md` §5).

## 4. Regression risk

New, fully isolated `features/model-playground/` and `services/model_playground/` — no existing feature's code is modified except:
- `frontend/lib/nav-registry.ts` (one new entry appended — low risk, purely additive per `02_UI.md` §2).
- `docs/Security.md`, `06_TECH_STACK.md`, `03_ARCHITECTURE.md`, `08_DEFINITION_OF_DONE.md` (documentation only, already updated alongside ADR-0010/0011 acceptance).

No shared component, no existing table, no existing route is touched. Regression risk for this phase is low and confined to "does the new nav entry render correctly," which is covered by manual verification above.

## 5. TODO

- [ ] Assign a phase owner.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
