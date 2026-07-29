# Model Playground — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Confirmed — filled in against [ADR-0011](../../decisions/0011-model-playground-provider-credential-security.md).
> **Last Updated:** 2026-07-29

---


## 1. New or modified tables

Three new tables, all in `backend/app/models/model_playground.py`:

**`ProviderCredential`**

| Column | Type | Notes |
|---|---|---|
| `id` | str (PK) | `new_id()`, same pattern as every other table |
| `provider` | str, indexed, unique | `"openai"` \| `"anthropic"` (per ADR-0012) — one credential per provider in v1, matching the spec's "configurable API keys per provider" (singular per provider, not multiple named credentials per provider) |
| `label` | str | user-facing name, defaults to the provider's display name if not given |
| `encrypted_api_key` | bytes | `VaultCrypto.encrypt_str()` output, per ADR-0011 §2.1 |
| `created_at` | datetime | |
| `updated_at` | datetime | bumped on key replacement |

**`PlaygroundRun`**

| Column | Type | Notes |
|---|---|---|
| `id` | str (PK) | |
| `prompt` | str (text, no arbitrary cap beyond a generous max length like Prompt Studio's `body`) | |
| `created_at` | datetime, indexed | for most-recent-first history ordering |

**`PlaygroundResult`**

| Column | Type | Notes |
|---|---|---|
| `id` | str (PK) | |
| `run_id` | str, FK → `playground_runs.id`, indexed | |
| `provider` | str | plain string snapshot, e.g. `"openai"` — **not** a FK to `ProviderCredential` (see §2) |
| `model` | str | e.g. `"gpt-4.1"`, `"claude-sonnet-5"` |
| `status` | str | `"success"` \| `"error"` \| `"timeout"` |
| `response_text` | str (text), nullable | null unless `status == "success"` |
| `error_message` | str, nullable | user-legible only, per spec FR8 — never a raw exception string |
| `latency_ms` | int, nullable | wall-clock time for this specific provider call |
| `prompt_tokens` / `completion_tokens` | int, nullable | only populated when the provider's API reports usage |
| `created_at` | datetime | |

## 2. Relationships

- `PlaygroundRun.results: list[PlaygroundResult]` — one-to-many, `cascade="all, delete-orphan"` (deleting a run deletes its results; same pattern as `Prompt.versions` in `models/prompt_studio.py`).
- `PlaygroundResult.provider`/`.model` are **plain string snapshots, not foreign keys** to `ProviderCredential` — this is deliberate (per spec FR4 / ADR-0011 §2.4): deleting a credential later must not cascade-delete or orphan past run results. A result row is a historical fact ("this run asked OpenAI's gpt-4.1"), independent of whether that provider is still configured.
- No relationship to any existing table (Secrets, Notes, Documents, Vault) — this is a fully standalone feature, consistent with [`01_SPEC.md`](01_SPEC.md) §4 ("does not reuse the Secrets feature's storage directly").

## 3. Migration plan

New Alembic migration, next in sequence after `0005_prompt_studio.py`: **`0006_model_playground.py`**, creating all three tables in one migration (they ship together, there's no reason to split them). Explicit `op.create_table(...)` calls, no direct schema edits — per [`03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2 and [`../../../docs/Database.md`](../../../docs/Database.md).

## 4. Data lifecycle

- **`ProviderCredential`**: persists until explicitly replaced or deleted by the user — same lifecycle class as Secrets (long-lived, user-managed), not scratch data.
- **`PlaygroundRun`/`PlaygroundResult`**: persist indefinitely, manual delete only — resolves [`01_SPEC.md`](01_SPEC.md) §6's non-blocking open question. A run is user-authored comparison data the user explicitly chose to keep (per spec FR10/FR11), not scratch conversion output like Ingest's temporary files, so no TTL/cleanup job is introduced.

## 5. TODO

- [ ] Confirm final table/column names during implementation if `04_DATABASE.md`'s proposed names collide with an existing naming convention check.
- [ ] Assign a phase owner.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/README.md](../../decisions/README.md)
- [../../decisions/0011-model-playground-provider-credential-security.md](../../decisions/0011-model-playground-provider-credential-security.md)
