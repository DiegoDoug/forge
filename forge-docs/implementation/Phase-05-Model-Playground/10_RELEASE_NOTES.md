# Model Playground — Release Notes

> **Purpose:** The release-facing summary of this phase — what shipped, what broke on purpose, what to do before upgrading. Written at RC, updated through sign-off; not a duplicate of `CURRENT_STATE.md` (the day-to-day working log) or `POST_IMPLEMENTATION_REVIEW.md` (the retrospective) — this is the document a user or another engineer reads to understand what changed, not how it was built.
> **Scope:** This phase only.
> **Status:** Release Candidate — owner sign-off recorded, pending PR merge/tag/freeze.
> **Version:** `v0.5.0-model-playground` (proposed, per the existing `vX.Y.Z-phase-name` tagging convention)
> **Last Updated:** 2026-07-29
> **Depends On:** [CURRENT_STATE.md](CURRENT_STATE.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md), [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)

---

## New Features

- A new **Model Playground** page (`/model-playground`), reachable from the sidebar and command palette, for testing and comparing LLM provider outputs side by side.
- UI-configurable, encrypted, per-provider API key storage for **OpenAI** and **Anthropic** — added, replaced, or removed entirely from the page itself, no environment variable or redeploy required. Keys are write-only after creation (never re-displayed, only replaced or removed).
- Send one prompt to multiple selected provider/model combinations in a single run; each provider/model call executes independently, so one failing or slow provider never blocks or blanks out the others.
- Each result panel shows the model used, latency, token usage (when the provider reports it), and a plain-language error message on failure or timeout.
- Persisted run history (indefinite retention, manual delete) — reopen or delete a past comparison at any time.
- New backend: `services/model_playground/` (credential CRUD, run orchestration with concurrent dispatch and per-target timeout/error isolation, OpenAI + Anthropic provider adapters behind a shared interface), 3 new tables (`provider_credentials`, `playground_runs`, `playground_results`), 8 new `/api/model-playground/*` endpoints.
- New `docs/Security.md` "Outbound network calls" section, documenting this phase's and Ingest's existing outbound-call posture in one place.

## Breaking Changes

None. No existing endpoint, page, table, or component was modified in a way that changes prior behavior — this phase adds new, fully isolated surface area. The one edit to an existing file beyond documentation (`backend/app/services/workbench.py`) is purely additive (one new entry in the pinned-tools registry, matching every prior phase's precedent — see Bug Fixes/Known Issues below for why this matters).

## Migrations

One new migration: `0006_model_playground.py`, adding `provider_credentials`, `playground_runs`, and `playground_results`. Additive only — no existing table or column is touched. Confirmed to apply cleanly on both a fresh install (`SQLModel.metadata.create_all` path) and an upgrade from `0005` (explicit `op.create_table` path, guarded by an existing-table check per the established pattern from `0005_prompt_studio.py`) — verified live against a real SQLite file during manual verification (`INFO [alembic.runtime.migration] Running upgrade 0005 -> 0006, Model Playground: ...` observed in the running backend's logs).

## Bug Fixes

None. This phase introduced no fix to already-shipped functionality — a genuinely clean, additive implementation with no found regressions in existing features (Secrets, Notes, Documents, Generators, Crypto, Converters, Utilities, Search, Prompt Studio, Workbench, Settings, Auth all continue to build/test/pass unchanged).

## Known Issues

- **Keyboard Enter/Space activation of a focused button could not be conclusively verified in this session's automated browser** — see [`QA/QA-0001-keyboard-activation-audit.md`](QA/QA-0001-keyboard-activation-audit.md). Tab order was confirmed correct; activation specifically could not be, because the automated tool's synthetic keyboard events reproduce a limitation Phase 01 independently documented over a month earlier (malformed `key` field on synthetic Enter/Space, defeating native `<button>` activation — see [`../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md`](../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md)). The identical non-activation reproduces on the pre-existing Secrets page, confirming this is a testing-tool property, not something this phase introduced. Tracked as a QA ticket, not a bug, per [`../../12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4.
- **Only two providers ship in v1 (OpenAI, Anthropic).** A generic "Custom / OpenAI-compatible" provider (self-hosted models, OpenRouter, etc.) was evaluated and explicitly deferred — see Deferred Work below. This is a documented scope boundary, not an oversight.

## Upgrade Notes

A normal `docker compose up --build` picks up the change: the new migration applies automatically on backend startup (same as every prior migration), no manual step, no data backfill, no new required environment variables. Model Playground itself is fully opt-in — with zero provider credentials configured, the page loads normally and shows both providers as "Not configured"; the rest of Forge is completely unaffected. Operators who want to use it configure an OpenAI and/or Anthropic API key from the page itself after upgrading.

## Deferred Work

- **A generic "Custom / OpenAI-compatible" pseudo-provider** (base-URL override, for self-hosted models or OpenRouter-style endpoints) — evaluated and explicitly deferred in [ADR-0011](../../decisions/0011-model-playground-provider-sdk-selection.md) §2.3, to keep v1's credential form and provider list simple. The adapter-interface design means adding it later is additive, not a rework, if real demand shows up.
- **Streaming (SSE) responses** — v1 waits for each provider's complete response; see [`01_SPEC.md`](01_SPEC.md) §5. Revisit once non-streaming is proven stable.
- **Multi-turn chat / conversation history within a run, cost estimation beyond echoing provider-reported token usage, revealing a stored credential's raw key** — all explicitly out of scope for v1, per [`01_SPEC.md`](01_SPEC.md) §5.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)
- [QA/README.md](QA/README.md)
- [../../decisions/0010-model-playground-provider-credential-security.md](../../decisions/0010-model-playground-provider-credential-security.md)
- [../../decisions/0011-model-playground-provider-sdk-selection.md](../../decisions/0011-model-playground-provider-sdk-selection.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
