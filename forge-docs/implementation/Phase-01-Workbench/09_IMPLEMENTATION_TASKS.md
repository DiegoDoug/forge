# Workbench — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md. Frozen alongside the rest of the specification per [ADR-0009](../../decisions/0009-phase-specification-freeze.md) — see IMPLEMENT.md before adding or changing a task.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Authorized — grouped into 4 milestones for checkpoint discipline
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_SPEC.md](01_SPEC.md), [IMPLEMENT.md](IMPLEMENT.md), [../../decisions/0009-phase-specification-freeze.md](../../decisions/0009-phase-specification-freeze.md)
> **Supersedes:** v0.1.0 of this document (same 16 tasks, grouped by number only, not by milestone content)

---

## 1. Task list

Grouped into the 4 milestones the project owner specified — each milestone is content-coherent (all-Foundation, all-Backend, all-Frontend, all-Integration), not just a numeric range. Checkpoint after every milestone, in addition to the standard 10–12 task / ~70% context triggers from [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1 — whichever comes first.

### Milestone 1 — Foundation (T1–T4)

- [ ] T1 — Vault → Secrets compatibility migration: rename UI copy/labels, routes (`/vault` → `/secrets`, old path aliased), `frontend/features/vault/` → `features/secrets/`, `backend/app/services/vault/` → `services/secrets/`, `backend/app/models/vault.py` → `secrets.py`, `backend/app/api/routes/vault.py` → `secrets.py` with `/api/vault` kept as a working alias. Database table renamed only if safe (per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)). — traces to `01_SPEC.md` FR13.
- [ ] T2 — Add the dedicated `/search` page, reusing the existing `GET /api/search` endpoint and `frontend/features/search/api.ts` unchanged. — traces to FR14, [ADR-0007](../../decisions/0007-search-dedicated-page.md).
- [ ] T3 — Write and apply the Alembic migration adding `workbench_layout` (per `04_DATABASE.md`). — traces to FR7.
- [ ] T4 — Frontend: the panel contract itself — `panel-types.ts` (`WorkbenchPanelDefinition`/`Metadata`/`Props`), `panel-registry.ts` (`registerWorkbenchPanel`, `getRegisteredPanels`), and the `register-all.ts` bootstrap stub (per `12_PANEL_INTERFACE.md` §2, §4). Nothing registers with it yet — this task only establishes the shared interface both backend validation (T7) and every panel (T11) build against.

**Checkpoint after T4.**

### Milestone 2 — Backend (T5–T8)

- [ ] T5 — `services/workbench.py`: `get_layout`, `update_layout`, `reset_layout`, and the `WORKBENCH_TOOL_KEYS` catalog (per `03_BACKEND.md` §2–3). — traces to FR6, FR7, FR8.
- [ ] T6 — `services/workbench.py`: `get_workbench()` aggregation (storage, recent activity, recent notes — no `recent_secrets` field) (per `03_BACKEND.md` §2). — traces to FR9, FR10.
- [ ] T7 — `api/routes/workbench.py`: `GET/PUT/POST /api/workbench*` routes and their Pydantic schemas, including structural (not enum) validation of `panels` and allowlist validation of `pinned_tools` (per `06_API.md`). — traces to FR1, FR2, FR7, FR8.
- [ ] T8 — Backend tests: `test_workbench.py` unit + integration tests (per `07_TESTING.md` §1) — including the panel-type-not-enum-validated test and the `recent_secrets`-absence regression check.

**Checkpoint after T8.**

### Milestone 3 — Frontend (T9–T12)

- [ ] T9 — The generic Workbench runtime: `WorkbenchGrid`, `WorkbenchPanelCard` (with error boundary), `WorkbenchEmptyState`, `WorkbenchResetButton`, `WorkbenchCustomizeToggle` (per `05_COMPONENTS.md` §1.1). — traces to FR3, FR4, FR8.
- [ ] T10 — `PinPickerDialog`, including disabled "coming soon" tiles for `prompt_studio`/`universal_converter`, driven by T5's tool catalog (per `05_COMPONENTS.md` §1.1, `02_UI.md` §3.4). — traces to FR6, FR9.
- [ ] T11 — The five active panels — `PinnedToolsPanel`, `RecentActivityPanel`, `QuickActionsPanel`, `SystemStatusPanel`, `RecentNotesPanel` — each implemented in its owning feature and registered via T4's registry, proving the extensibility contract by construction (per `05_COMPONENTS.md` §1.2, `08_ACCEPTANCE.md` §6). — traces to FR3, FR9, FR10, FR11, FR15.
- [ ] T12 — Drag-and-drop panel reordering + keyboard-only fallback, pin/unpin reordering, and every panel's empty/loading/error states plus the all-hidden empty state (per `02_UI.md` §3.1–3.3). — traces to FR5, FR6.

**Checkpoint after T12.**

### Milestone 4 — Integration (T13–T16)

- [ ] T13 — Sidebar and command-palette entries rename Dashboard → Workbench; wire route `/` to the new Workbench page (per `02_UI.md` §2). — traces to FR1, FR12.
- [ ] T14 — Remove `frontend/features/dashboard/` and the old `/api/dashboard` route entirely (direct cutover, per `06_API.md` §1 note).
- [ ] T15 — Manual verification pass: functional, performance (render time, drag FPS, layout-save latency, re-render check), and accessibility (keyboard walkthrough, focus management, screen-reader spot check) per `07_TESTING.md` §3.
- [ ] T16 — Automated accessibility scan (axe or equivalent) against Workbench (both modes) and `/search`, then a full pass against `08_ACCEPTANCE.md` before declaring the phase done.

**Final Validation after T16** — every criterion in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) checked, including §7's ADR-acceptance guard (no capability registry, no `ProjectProvider`, no workflow code introduced).

## 2. Task ordering notes

- **Milestone boundaries are hard checkpoints**, not just numbering — don't start T5 before T1–T4 are done, even if it seems faster to parallelize; the checkpoint at each boundary is a deliberate recovery point per the project owner's implementation strategy.
- **T1 and T2 come first within Foundation** — the default pinned-tools set (FR9) and Quick Actions' "new secret" action depend on the Secrets rename existing.
- **T4 (the panel contract) must exist before T7** (backend validates against its *shape*, not its enum — see `06_API.md`'s note that panel `type` isn't enum-validated) **and before T11** (every panel registers against it).
- **T5 before T6 before T7** — layout persistence, then aggregation, then the routes that expose both.
- **T9 before T10 and T11** — panels and the pin picker render inside `WorkbenchPanelCard` / the grid, which must exist first.
- **T13 depends on T9–T11 being functionally complete** — the sidebar/palette rename should land after the page it points to actually renders something real.
- **T14 (removing the old Dashboard) is last** among implementation tasks — nothing deletes the fallback until Milestone 3's replacement is proven working.
- **T15 and T16 are the closing verification pass**, feeding directly into `08_ACCEPTANCE.md` and the phase's Definition of Success (`README.md`).

## 3. TODO

- [ ] TODO: Re-split any task that turns out too large once implementation starts — per [ADR-0009](../../decisions/0009-phase-specification-freeze.md) §2, this counts as a "clarification," not scope expansion, as long as the total work covered doesn't change.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../decisions/0009-phase-specification-freeze.md](../../decisions/0009-phase-specification-freeze.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
