# Checkpoint — Phase 01 Workbench — 2026-07-21

> **Trigger:** Milestone completion (Milestone 1 — Foundation, T1–T4)
> **Phase:** [Phase-01-Workbench](../implementation/Phase-01-Workbench/README.md)
> **Last Updated:** 2026-07-21

---

## Completed Tasks

- [x] T1 — Vault → Secrets compatibility migration ([ADR-0006](../decisions/0006-vault-renamed-to-secrets.md)). Merged via [#6](https://github.com/DiegoDoug/forge/pull/6).
- [x] T2 — Dedicated `/search` page ([ADR-0007](../decisions/0007-search-dedicated-page.md)). Merged via [#7](https://github.com/DiegoDoug/forge/pull/7).
- [x] T3 — `workbench_layout` Alembic migration ([04_DATABASE.md](../implementation/Phase-01-Workbench/04_DATABASE.md)). Merged via [#8](https://github.com/DiegoDoug/forge/pull/8).
- [x] T4 — The panel contract ([12_PANEL_INTERFACE.md](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §2, §4). This checkpoint.

## Modified Files

**T1 (Vault → Secrets):**
- `backend/app/models/vault.py` → `secrets.py`, `backend/app/schemas/vault.py` → `secrets.py`, `backend/app/services/vault/` → `services/secrets/`, `backend/app/api/routes/vault.py` → `secrets.py`
- `backend/app/api/router.py`, `backend/app/models/__init__.py`, `backend/app/services/dashboard.py`, `backend/app/services/search/service.py`, `backend/app/services/settings/backup.py`
- `frontend/features/vault/` → `frontend/features/secrets/`, `frontend/app/(app)/vault/` → `frontend/app/(app)/secrets/`
- `frontend/next.config.ts`, `frontend/lib/nav-registry.ts`, `frontend/components/command-palette/command-palette-provider.tsx`, `frontend/app/(app)/page.tsx`, `frontend/app/layout.tsx`, `frontend/app/(auth)/setup/page.tsx`, `frontend/app/(app)/settings/page.tsx`
- `README.md`, `.env.example`, `docs/API.md`, `docs/FolderStructure.md`, `docs/Database.md`, `docs/Contributing.md`, `docs/Architecture.md`, `docs/Security.md`, `docs/Deployment.md`, `docs/Roadmap.md`, `docs/DecisionLog.md`

**T2 (Search page):**
- `frontend/app/(app)/search/page.tsx` (new), `frontend/features/search/search-result-list.tsx` (new)

**T3 (workbench_layout migration):**
- `backend/app/models/workbench.py` (new), `backend/app/models/__init__.py`, `backend/alembic/versions/0003_workbench_layout.py` (new)
- `forge-docs/implementation/Phase-01-Workbench/04_DATABASE.md`, `docs/Database.md`

**T4 (Panel contract):**
- `frontend/features/workbench/panel-types.ts` (new), `frontend/features/workbench/panel-registry.ts` (new), `frontend/features/workbench/register-all.ts` (new)

**Tracking docs updated throughout:**
- `forge-docs/implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md`, `forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md`

## Current State

Milestone 1 (Foundation) is fully done and merged to `master` (T1–T3 via PRs #6–#8; T4 on branch `feature/t4-panel-contract`, about to merge). Concretely, a fresh session can rely on:

- **Secrets** (formerly Vault) is the live feature name everywhere — routes, modules, UI copy. `/api/vault` and the frontend `/vault` route still resolve as temporary compatibility aliases (real debt, tracked in Known Issues below).
- A dedicated `/search` page exists at `frontend/app/(app)/search/page.tsx`, reusing the existing `GET /api/search` endpoint unchanged. It is not in the sidebar nav — only reachable via the command palette today (the Pinned Tools panel will be the other path once T10/T11 land).
- The `workbench_layout` table exists in the database (single row, `id=1`, `panels`/`pinned_tools` JSON-in-TEXT columns), created by Alembic migration `0003`. Nothing reads or writes it yet — that's T5.
- The panel contract (`WorkbenchPanelDefinition`/`Metadata`/`Props`, `registerWorkbenchPanel`/`getRegisteredPanels`) exists at `frontend/features/workbench/`, but nothing implements it and nothing calls `getRegisteredPanels()` yet. `register-all.ts` is an empty stub, not yet imported anywhere.
- There is no Workbench UI yet — the home page (`/`) is still the old Dashboard, unchanged. Milestone 2 (backend) and Milestone 3 (frontend) build the actual replacement; Milestone 4 does the cutover and removes the old Dashboard.

## Remaining Work

- **Milestone 2 — Backend (T5–T8):** `services/workbench.py` (layout persistence + `WORKBENCH_TOOL_KEYS` catalog + `get_workbench()` aggregation), `api/routes/workbench.py` (the three `/api/workbench*` routes and Pydantic schemas), and `test_workbench.py`.
- **Milestone 3 — Frontend (T9–T12):** the generic runtime (`WorkbenchGrid`, `WorkbenchPanelCard`, etc.), `PinPickerDialog`, the five active panels (this is where panels actually call `registerWorkbenchPanel`), and drag/keyboard reordering.
- **Milestone 4 — Integration (T13–T16):** nav/palette rename to Workbench, old Dashboard removal, manual verification, and the accessibility scan.

## Recommended Next Prompt

```
You are working in the Forge repository as a Claude Code session.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-01-Workbench/README.md
3. forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md
4. forge-docs/implementation/Phase-01-Workbench/IMPLEMENT.md
5. This checkpoint (forge-docs/history/2026-07-21-phase-01-milestone-1-foundation.md)

Milestone 1 (Foundation, T1-T4) is complete. Begin work on: T5 in
09_IMPLEMENTATION_TASKS.md (services/workbench.py: get_layout, update_layout,
reset_layout, and the WORKBENCH_TOOL_KEYS catalog, per 03_BACKEND.md 2-3),
the first task of Milestone 2 -- Backend.

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly,
plus the milestone checkpoints in IMPLEMENT.md -- stop after T8 (end of
Milestone 2) even if the 10-12 task threshold hasn't been hit yet.

The specification is locked per forge-docs/decisions/0009-phase-specification-freeze.md.
Only bug fixes, clarifications, and typo corrections are in scope beyond the
documented tasks -- anything else (extra panels, workflows, a command palette,
a capability registry, a Projects interface, a plugin system, AI additions)
gets flagged and deferred, not built.
```

## Known Risks

- **Temporary compatibility aliases from T1** (`/api/vault` backend proxy, frontend `/vault` → `/secrets` redirect) are real debt per ADR-0006 §4 — no removal task is scheduled yet; needs a future cleanup task once nothing external depends on the old path.
- **`WorkbenchPanelPrecondition`'s exact shape** (used by the optional `permissions` metadata field) wasn't pinned down in `12_PANEL_INTERFACE.md` — a minimal `{ description, check }` shape was defined since no Phase 01 panel populates it. Revisit if a future panel (e.g. Model Playground) actually needs preconditions — the shape may need to change, which is a non-breaking change today since nothing depends on it.
- **`register-all.ts` is not yet wired into the app shell.** This is intentional (nothing to register yet), but it means T9 must remember to both import it from the app shell *and* start having panels import their own registration modules from it — easy to forget one half.
- **Milestone 2 (T5–T7) touches the backend tool catalog** (`WORKBENCH_TOOL_KEYS`), which must use `"secrets"` as the key (not `"vault"`) per ADR-0006 — already called out in `06_API.md` §5 as resolved, but worth double-checking during T5 implementation since it's an easy place for the pre-rename name to leak back in.
- **Doc-prose consistency deferred from T1**: some older, purely descriptive mentions of "vault"/"Vault" in `docs/Deployment.md`, `docs/Security.md`, `docs/Roadmap.md`, and `docs/DecisionLog.md` were deliberately left as-is where they weren't a proper-noun reference to the feature name. Not a functional gap, but flagged in `CURRENT_STATE.md`'s Known Issues in case a future pass wants full consistency.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-01-Workbench/CURRENT_STATE.md](../implementation/Phase-01-Workbench/CURRENT_STATE.md)
- [../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md](../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md)
