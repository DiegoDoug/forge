# Workbench — Current State

> **Purpose:** Live snapshot of where this phase actually stands, updated at every checkpoint.
> **Scope:** This phase only — updated continuously, never left stale.
> **Ownership:** TODO — assign a phase owner.
> **Status:** In progress — Milestone 1 (Foundation) complete, Milestone 2 (Backend) underway (T5 done)
> **Version:** 0.4.0
> **Last Updated:** 2026-07-21
> **Depends On:** [README.md](README.md), [IMPLEMENT.md](IMPLEMENT.md)
> **Supersedes:** v0.2.0 of this document (pre-implementation)

---


## Current Status

**Milestone 1 (Foundation) complete — T1–T4 all done.** Specification is locked ([ADR-0009](../../decisions/0009-phase-specification-freeze.md)). See [`../../history/2026-07-21-phase-01-milestone-1-foundation.md`](../../history/2026-07-21-phase-01-milestone-1-foundation.md) for the Milestone 1 checkpoint record. **Milestone 2 (Backend) is underway: T5 done, T6–T8 remaining.** Work is on branch `feature/t5-workbench-layout-service`.

**Clarification (T5):** `03_BACKEND.md` §1 describes the Dashboard→Workbench move as a rename "in place." In practice `backend/app/services/dashboard.py` (and `/api/dashboard`) must keep working until T14 explicitly removes them (per `09_IMPLEMENTATION_TASKS.md` T14 and its ordering note "nothing deletes the fallback until Milestone 3's replacement is proven working") — so T5 added `backend/app/services/workbench.py` as a new module alongside `dashboard.py`, not a literal file rename. `dashboard.py`/`get_dashboard()` are untouched. T6 will add `get_workbench()` aggregation to the new module (superseding `get_dashboard()`'s data shape per `01_SPEC.md`), and the literal old-file removal happens at T14 as scheduled. This is a clarification of already-locked spec text, not a scope change, per ADR-0009 §2.

## Completed

- [x] T1 — Vault → Secrets compatibility migration ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)). Database tables were already named `secrets`/`folders`/`tags`/`secret_versions`/`secret_tag_links` before this task, so no data migration was needed — the rename was scoped entirely to module paths, routes, and UI copy:
  - Backend: `app/models/vault.py` → `secrets.py`, `app/schemas/vault.py` → `secrets.py`, `app/services/vault/` → `services/secrets/`, `app/api/routes/vault.py` → `secrets.py`. All cross-feature imports (`dashboard.py`, `search/service.py`, `settings/backup.py`, `models/__init__.py`) updated.
  - API: the `secrets` router is mounted at both `/api/secrets` and `/api/vault` in `app/api/router.py` (same router object, same handlers — not a second implementation), per ADR-0006 §2's compatibility-alias requirement.
  - Frontend: `features/vault/` → `features/secrets/` (`vault-filters.tsx` → `secrets-filters.tsx`, `vaultApi` → `secretsApi`, `useVaultMutations` → `useSecretsMutations`), `app/(app)/vault/` → `app/(app)/secrets/`. `next.config.ts` adds a `/vault` → `/secrets` redirect (temporary, `permanent: false`) so the old route resolves instead of 404ing. `nav-registry.ts`, the command palette, the dashboard home page, the setup page, and the settings page all updated to the new label/route.
  - Shipped-app docs (`README.md`, `docs/API.md`, `docs/FolderStructure.md`, `docs/Database.md`, `docs/Contributing.md`, `docs/Architecture.md`, `docs/Security.md`, `docs/Deployment.md`, `docs/Roadmap.md`, `docs/DecisionLog.md`, `.env.example`) updated to reflect the new name; a new `docs/DecisionLog.md` entry records the alias approach and that both aliases are temporary.
  - `backend/app/core/security.py`'s `VaultCrypto`/`get_vault_crypto` were deliberately **not** renamed — they're a generic at-rest-encryption utility, not part of the Vault→Secrets feature rename ADR-0006 scopes (its file-path list doesn't include `core/security.py`), and renaming them would ripple into `test_security.py` for no behavioral benefit.
- [x] T2 — Dedicated `/search` page ([ADR-0007](../../decisions/0007-search-dedicated-page.md)). No backend change — reuses `GET /api/search` and `frontend/features/search/api.ts` unchanged.
  - `frontend/app/(app)/search/page.tsx` (`SearchPage`): route `/search`, query param `?q=` kept in sync via `router.replace`. States per `02_UI.md` §3.5: query length ≤1 shows a prompt empty state, loading shows skeleton rows, a failed fetch shows an inline error with a Retry button (`resultsQuery.refetch()`), otherwise renders results.
  - `frontend/features/search/search-result-list.tsx` (`SearchResultList`): renders the same secrets/notes/documents groups the command palette shows, linking to each item's `?open=id` detail view; a true empty result set shows `No matches for "<query>"` per spec.
  - Not added to `frontend/lib/nav-registry.ts` — per `02_UI.md`, `/search` is reachable only via the (future) Pinned Tools panel and the command palette, not a permanent sidebar item.
- [x] T3 — `workbench_layout` Alembic migration ([04_DATABASE.md](04_DATABASE.md)). `backend/app/models/workbench.py` (`WorkbenchLayout`, single-row `id=1` pattern matching `AppConfig`) registered in `models/__init__.py`; `backend/alembic/versions/0003_workbench_layout.py` creates the table with the same idempotent existence-guard `0002_documents.py` uses (a no-op on fresh installs, since `0001`'s `create_all()` already covers it once the model is registered). No data migration — the row is created lazily on first access, per the service layer T5 will add. Verified fresh-install and incremental upgrade/downgrade paths directly against a scratch SQLite DB; full pytest suite (32 tests) still green. `docs/Database.md` and `04_DATABASE.md` updated to record it.
- [x] T4 — The panel contract ([12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md) §2, §4). Three new files under `frontend/features/workbench/`:
  - `panel-types.ts` — `WorkbenchPanelDefinition`, `WorkbenchPanelMetadata`, `WorkbenchPanelProps`, matching the interface literally as specified. Also defines `WorkbenchPanelPrecondition` (`{ description, check }`) for the optional `permissions` field, whose concrete shape the spec never pins down — a clarification, not a design change, since no Phase 01 panel populates it.
  - `panel-registry.ts` — `registerWorkbenchPanel(definition)`/`getRegisteredPanels()`, backed by a `Map<string, WorkbenchPanelDefinition>`.
  - `register-all.ts` — an empty bootstrap stub. **Not yet imported from the app shell** — nothing registers with it yet (by design, per the task's own scope note), and wiring it in only becomes meaningful once `WorkbenchGrid` (T9) actually calls `getRegisteredPanels()`.
  - Verified with `tsc --noEmit` and `eslint`; no runtime behavior exists yet to browser-verify (pure types + an unused registry).
- [x] T5 — `services/workbench.py`: `get_layout`, `update_layout`, `reset_layout`, `WORKBENCH_TOOL_KEYS` ([03_BACKEND.md](03_BACKEND.md) §2–3). New module (see "Clarification (T5)" above — `dashboard.py` is untouched). `get_layout` mirrors `settings/service.py`'s `get_config()` get-or-create pattern, seeding the first-access row with the real default panels/pinned-tools (`DEFAULT_LAYOUT_PANELS`/`DEFAULT_PINNED_TOOLS`), not empty arrays. `update_layout` validates panel shape (non-empty string `type`, boolean `visible`, no duplicate `type`) and pinned-tool keys against `WORKBENCH_TOOL_KEYS`, raising `AppError(status_code=422)` on failure per [06_API.md](06_API.md) §3. `reset_layout` overwrites both columns with the same default constants. Verified against an in-memory SQLite DB (create-on-first-access, idempotency, custom-layout persistence, all three validation-failure paths, reset-restores-defaults) plus the full existing pytest suite (32 tests, unaffected). No dedicated test file yet — that's T8.

## In Progress

- [ ] TODO: nothing in progress right now. T6 (`get_workbench()` aggregation in `services/workbench.py`) is next.

## Remaining

- [ ] T6–T16 in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — rest of Milestone 2 (Backend), then Milestones 3 (Frontend) and 4 (Integration).

## Known Issues

- [ ] Temporary compatibility aliases from T1 are debt, per ADR-0006 §4: `/api/vault` (backend proxy) and the frontend `/vault` → `/secrets` redirect both need a later cleanup task to remove once nothing external depends on the old path.
- [ ] Lower-priority prose in `docs/Deployment.md`/`docs/Security.md`/`docs/Roadmap.md`/`docs/DecisionLog.md`'s older entries was updated where it named the feature ("Vault"/"vault secret") but generic descriptive phrasing was left untouched where it wasn't clearly a proper-noun reference to the feature — not a gap, a deliberate line per this task's scope, but flagging in case a future pass wants full consistency.

## Architectural Decisions

- [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md) — Workbench replaces Dashboard.
- [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) — Workbench uses a panel architecture.
- [ADR-0003](../../decisions/0003-workbench-single-row-layout.md) — Single-row persisted layout.
- [ADR-0004](../../decisions/0004-interactive-workflows-not-automation.md) — Interactive workflows, not automation.
- [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) — Projects become the primary organizational unit.
- [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md) — Vault renamed to Secrets.
- [ADR-0007](../../decisions/0007-search-dedicated-page.md) — Search becomes a dedicated Workbench-reachable page.

- [ADR-0009](../../decisions/0009-phase-specification-freeze.md) — Phase Specification Freeze.

All eight are `Status: Accepted` as of 2026-07-20. [ADR-0008](../../decisions/0008-capability-registry-direction.md) (Capability Registry) was also proposed during this phase's planning and deliberately left `Status: Proposed` — not a Phase 01 dependency, revisit later per its own trigger condition. No code has been written against any ADR yet.

## Modified Files

- [x] `backend/app/models/vault.py` → `backend/app/models/secrets.py`
- [x] `backend/app/models/__init__.py`
- [x] `backend/app/schemas/vault.py` → `backend/app/schemas/secrets.py`
- [x] `backend/app/services/vault/` → `backend/app/services/secrets/` (`__init__.py`, `service.py`)
- [x] `backend/app/api/routes/vault.py` → `backend/app/api/routes/secrets.py`
- [x] `backend/app/api/router.py`
- [x] `backend/app/services/dashboard.py`
- [x] `backend/app/services/search/service.py`
- [x] `backend/app/services/settings/backup.py`
- [x] `frontend/features/vault/` → `frontend/features/secrets/` (`api.ts`, `secret-detail-sheet.tsx`, `secret-form-dialog.tsx`, `secret-types.ts`, `vault-filters.tsx` → `secrets-filters.tsx`)
- [x] `frontend/app/(app)/vault/` → `frontend/app/(app)/secrets/` (`page.tsx`)
- [x] `frontend/next.config.ts` (added `/vault` → `/secrets` redirect)
- [x] `frontend/lib/nav-registry.ts`
- [x] `frontend/components/command-palette/command-palette-provider.tsx`
- [x] `frontend/app/(app)/page.tsx`
- [x] `frontend/app/layout.tsx`
- [x] `frontend/app/(auth)/setup/page.tsx`
- [x] `frontend/app/(app)/settings/page.tsx`
- [x] `README.md`, `.env.example`, `docs/API.md`, `docs/FolderStructure.md`, `docs/Database.md`, `docs/Contributing.md`, `docs/Architecture.md`, `docs/Security.md`, `docs/Deployment.md`, `docs/Roadmap.md`, `docs/DecisionLog.md`
- [x] `forge-docs/implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md` (T1–T4 checked off)
- [x] `frontend/app/(app)/search/page.tsx` (new)
- [x] `frontend/features/search/search-result-list.tsx` (new)
- [x] `backend/app/models/workbench.py` (new)
- [x] `backend/app/models/__init__.py`
- [x] `backend/alembic/versions/0003_workbench_layout.py` (new)
- [x] `forge-docs/implementation/Phase-01-Workbench/04_DATABASE.md` (TODOs checked off)
- [x] `docs/Database.md` (`workbench_layout` row added)
- [x] `frontend/features/workbench/panel-types.ts` (new)
- [x] `frontend/features/workbench/panel-registry.ts` (new)
- [x] `frontend/features/workbench/register-all.ts` (new)
- [x] `forge-docs/history/2026-07-21-phase-01-milestone-1-foundation.md` (new — this checkpoint)
- [x] `backend/app/services/workbench.py` (new)
- [x] `forge-docs/implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md` (T5 checked off)

## Next Milestone

Milestone 2 — Backend (T5–T8): layout persistence service, workbench aggregation, API routes, backend tests. See [`IMPLEMENT.md`](IMPLEMENT.md) "Milestone Plan" and [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Next Claude Prompt

```
You are working in the Forge repository as a Claude Code session.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-01-Workbench/README.md
3. forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md
4. forge-docs/implementation/Phase-01-Workbench/IMPLEMENT.md
5. forge-docs/history/2026-07-21-phase-01-milestone-1-foundation.md

Milestone 1 (Foundation, T1-T4) is complete. Begin work on: T5 in
09_IMPLEMENTATION_TASKS.md (services/workbench.py: get_layout, update_layout,
reset_layout, and the WORKBENCH_TOOL_KEYS catalog, per 03_BACKEND.md 2-3),
the first task of Milestone 2 — Backend.

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly,
plus the milestone checkpoints in IMPLEMENT.md — stop after T8 (end of
Milestone 2) even if the 10-12 task threshold hasn't been hit yet.

The specification is locked per forge-docs/decisions/0009-phase-specification-freeze.md.
Only bug fixes, clarifications, and typo corrections are in scope beyond the
documented tasks — anything else (extra panels, workflows, a command palette,
a capability registry, a Projects interface, a plugin system, AI additions)
gets flagged and deferred, not built.
```

## Session Notes

- 2026-07-20 — Phase scaffold created by the Lead Architect FDK setup. No implementation work has occurred.
- 2026-07-20 — Full spec pass: `01_SPEC.md` through `08_ACCEPTANCE.md` and new `12_PANEL_INTERFACE.md` drafted; ADR-0001 through ADR-0007 recorded and accepted; `README.md` Exit Criteria added. Still no implementation work — every exit-criteria item needs project-owner confirmation before `IMPLEMENT.md` is authorized.
- 2026-07-20 — Scope-freeze pass: Secrets rename refined to a compatibility migration (ADR-0006 v0.2.0); Search's scope confirmed as page-only, with a future command-palette direction recorded but deferred (ADR-0007 §6); Capability Registry direction recorded as ADR-0008, deliberately `Proposed` not `Accepted`; Projects interface confirmed deferred to Phase 06 (ADR-0005 unchanged); Workflows explicitly excluded from this phase. All nine Exit Criteria documents are now content-complete. `09_IMPLEMENTATION_TASKS.md` populated with an ordered 16-task breakdown. `IMPLEMENT.md` remains "Not authorized" pending the project owner's explicit go-ahead.
- 2026-07-20 — **Authorized.** ADR-0009 (Phase Specification Freeze) recorded and accepted. `09_IMPLEMENTATION_TASKS.md` regrouped into 4 content-coherent milestones (Foundation/Backend/Frontend/Integration). `IMPLEMENT.md` updated with the milestone checkpoint plan and the immutable Priority Order rule (Correctness > Existing functionality > Stability > Performance > UX polish > New functionality). `README.md` now carries a Definition of Success and a formal Authorization record. Specification is locked; implementation is approved to begin at T1.
- 2026-07-21 — **T1 complete** (branch `feature/t1-vault-secrets-migration`, merged to `master` via [#6](https://github.com/DiegoDoug/forge/pull/6)). Vault → Secrets compatibility migration executed per ADR-0006: database tables were already correctly named, so the work was module/route/UI renames plus two temporary aliases (`/api/vault` proxy, frontend `/vault` redirect). See "Completed" above for the full file list.
- 2026-07-21 — **T2 complete** (branch `feature/t2-search-page`, merged to `master` via [#7](https://github.com/DiegoDoug/forge/pull/7)). Dedicated `/search` page added per ADR-0007, reusing `GET /api/search` and `frontend/features/search/api.ts` unchanged — no backend change.
- 2026-07-21 — **T3 complete** (branch `feature/t3-workbench-layout-migration`, merged to `master` via [#8](https://github.com/DiegoDoug/forge/pull/8)). `workbench_layout` Alembic migration written and verified per `04_DATABASE.md`.
- 2026-07-21 — **T4 complete, Milestone 1 (Foundation) checkpoint** (branch `feature/t4-panel-contract`). The panel contract (`panel-types.ts`, `panel-registry.ts`, `register-all.ts`) added per `12_PANEL_INTERFACE.md` §2, §4 — establishes the interface, nothing registers yet. Full checkpoint logged to `../../history/2026-07-21-phase-01-milestone-1-foundation.md` per `10_CHECKPOINT_PROTOCOL.md`. Milestone 2 (Backend, T5–T8) is next.
- 2026-07-21 — **T5 complete** (branch `feature/t5-workbench-layout-service`, Milestone 2 underway). `backend/app/services/workbench.py` added with `get_layout`/`update_layout`/`reset_layout` and `WORKBENCH_TOOL_KEYS` per `03_BACKEND.md` §2–3. Clarified during implementation that this is a new module alongside `dashboard.py`, not a literal rename, since `dashboard.py`/`/api/dashboard` must stay live until T14 — see "Clarification (T5)" above. No checkpoint doc yet; per `IMPLEMENT.md`'s Milestone Plan the next checkpoint lands after T8.

## Cross-references

- [README.md](README.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
- [../../history/README.md](../../history/README.md)
