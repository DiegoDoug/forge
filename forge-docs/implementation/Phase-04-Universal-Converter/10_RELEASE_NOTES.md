# Universal Converter — Release Notes

> **Purpose:** The release-facing summary of this phase — what shipped, what broke on purpose, what to do before upgrading. Written at RC (Milestone 7), updated through sign-off; not a duplicate of `CURRENT_STATE.md` (the day-to-day working log) — this is the document a user or another engineer reads to understand what changed, not how it was built.
> **Scope:** This phase only.
> **Status:** Draft — filled in at RC (Milestone 7, T20e). Finalized at the Released stage per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), after Owner Sign-off.
> **Version:** [tag this phase ships as, e.g. `v0.4.0-universal-converter` — TODO: confirm exact tag with the project owner at sign-off]
> **Last Updated:** 2026-07-25
> **Depends On:** [CURRENT_STATE.md](CURRENT_STATE.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md)

---

## New Features

- One unified **Converter** page (`/converters`) replaces the two previously separate Converters and Ingest pages: a "Text & Data" section (JSON, YAML, XML, CSV, regex, URL/Unicode, cron, timestamp, diff — unchanged) and a "Documents" section (file → Markdown conversion — unchanged), presented together for the first time.
- A single sidebar/command-palette entry ("Converter") replaces the previous two ("Converters", "Ingest").
- The old `/ingest` URL redirects to `/converters` — existing bookmarks and links keep working.
- A new backend `ConverterProvider` interface and registry (`backend/app/services/converters/providers/`) — additive scaffolding so a future conversion direction can register as a new provider rather than requiring its own page. The existing document pipeline is registered as `MarkItDownProvider`, a pure delegation wrapper with zero behavior change of its own.
- A new, additive endpoint: `GET /api/converters/providers`, listing registered providers and their supported formats.

## Breaking Changes

None. Every existing endpoint (`/api/ingest/*`, `POST /api/converters/cron/parse`) keeps its exact path, request shape, response shape, and status codes — confirmed by contract-preservation tests, not just assumed. The `/ingest` page itself is retired, but the URL redirects rather than 404ing.

## Migrations

None. This phase introduces zero new database tables and zero schema changes — confirmed: `backend/alembic/versions/` is unchanged (still `0001`–`0005`), and a fresh-volume Docker boot applied only the five pre-existing migrations.

## Bug Fixes

- **Workbench's default pinned-tools list would have silently broken.** Discovered while consolidating the nav entry: Workbench (Phase 01) carried a dead-code-in-waiting dependency — `"ingest"` was the *first* item in `DEFAULT_PINNED_TOOLS` (meaning every fresh install pins it by default), and a forward-looking `"universal_converter"` placeholder anticipated this exact phase. Retiring the `/ingest` nav entry without also updating Workbench's own nav-to-pinned-tool mapping would have left every fresh install with a silently-missing pinned tile (the lookup fails soft to nothing, not a crash). Fixed by retiring both the dead `"ingest"` key and the redundant `"universal_converter"` placeholder in favor of the existing `"converters"` key — live-verified: the Workbench pinned-tools panel correctly shows a "Converter" tile, both in dev and in a fresh Docker Compose boot.

## Known Issues

- **Image files (`.jpg`/`.png`/etc.) with no vision-LLM assistance configured (the default) fail to convert** — MarkItDown produces no extractable text without captioning help, so the conversion errors out rather than producing empty or placeholder output. This is pre-existing Ingest behavior, not something this phase introduced or changed; it's now pinned by a test (`test_ingest_pipeline.py::test_convert_image_without_vision_fails_with_no_text_content`) instead of being an undocumented surprise. Tracked as an honest gap, not a regression — enabling vision assistance (`FORGE_VISION_ENABLED`) is the existing workaround.
- **`npm ci` fails against this repository's current lockfile** (a pre-existing, unrelated condition, already documented in `frontend/Dockerfile`'s own comment: the lockfile has Windows-generated optional-dependency entries that don't cover every platform). Discovered while building this phase's reproducibility check (Milestone 7, T20a) — not caused by this phase (`package.json`/`package-lock.json` are both byte-for-byte unchanged), and the production Docker build already correctly works around it via `npm install` instead of `npm ci`. Flagged here for visibility since it would affect any future CI pipeline that assumes `npm ci` works.

## Upgrade Notes

No special upgrade steps. A normal `docker compose up --build` picks up the change; no new environment variables, no manual migration step, no data backfill. Anyone with `/ingest` bookmarked will be redirected to `/converters` automatically.

## Deferred Work

- **Any new conversion direction** (e.g. Markdown → DOCX/PDF, server-side JSON ↔ YAML ↔ XML round-trips) — this phase is explicitly consolidation-only; see [`01_SPEC.md`](01_SPEC.md) §5. The new `ConverterProvider` registry exists specifically so a future phase can add one without re-architecting the page.
- **Moving the client-side text tools to the backend** — confirmed with the project owner they stay client-side; only the presentation layer unified.
- **Conversion history/presets persistence** — file-based conversion keeps Ingest's exact ephemeral, TTL-cleaned model; no new database table.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
