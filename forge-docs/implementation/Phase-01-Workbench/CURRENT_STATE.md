# Workbench — Current State

> **Purpose:** Live snapshot of where this phase actually stands, updated at every checkpoint.
> **Scope:** This phase only — updated continuously, never left stale.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Authorized, not yet started
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [README.md](README.md), [IMPLEMENT.md](IMPLEMENT.md)
> **Supersedes:** v0.1.0 of this document (pre-authorization)

---


## Current Status

**In progress — Milestone 1 (Foundation) underway.** Specification is locked ([ADR-0009](../../decisions/0009-phase-specification-freeze.md)). T1 and T2 are complete; T3–T4 have not been started. Work is on branch `feature/t2-search-page`.

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

## In Progress

- [ ] TODO: nothing in progress yet — T3 (the `workbench_layout` Alembic migration) is next per the milestone ordering notes in `09_IMPLEMENTATION_TASKS.md` §2.

## Remaining

- [ ] T3–T16 in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — the rest of Milestone 1 (Foundation), then Milestones 2–4.

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
- [x] `forge-docs/implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md` (T1, T2 checked off)
- [x] `frontend/app/(app)/search/page.tsx` (new)
- [x] `frontend/features/search/search-result-list.tsx` (new)

## Next Milestone

Milestone 1 — Foundation (T1–T4): Secrets compatibility migration (done), `/search` page (done), `workbench_layout` migration, the panel contract. See [`IMPLEMENT.md`](IMPLEMENT.md) "Milestone Plan" and [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Next Claude Prompt

```
You are working in the Forge repository as a Claude Code session, on branch
feature/t2-search-page.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-01-Workbench/README.md
3. forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md
4. forge-docs/implementation/Phase-01-Workbench/IMPLEMENT.md

T1 and T2 are complete. Begin work on: T3 in 09_IMPLEMENTATION_TASKS.md (write
and apply the Alembic migration adding workbench_layout, per 04_DATABASE.md),
the third task of Milestone 1 — Foundation.

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly,
plus the milestone checkpoints in IMPLEMENT.md — stop after T4 (end of
Milestone 1) even if the 10-12 task threshold hasn't been hit yet.

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
- 2026-07-21 — **T2 complete** (branch `feature/t2-search-page`). Dedicated `/search` page added per ADR-0007, reusing `GET /api/search` and `frontend/features/search/api.ts` unchanged — no backend change. Milestone 1 is not yet checkpoint-complete — T3–T4 remain.

## Cross-references

- [README.md](README.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
- [../../history/README.md](../../history/README.md)
