# Checkpoint — Phase 01 Workbench — 2026-07-21

> **Trigger:** Milestone completion (Milestone 2 — Backend, T5–T8)
> **Phase:** [Phase-01-Workbench](../implementation/Phase-01-Workbench/README.md)
> **Last Updated:** 2026-07-21

---

## Completed Tasks

- [x] T5 — `services/workbench.py`: `get_layout`, `update_layout`, `reset_layout`, `WORKBENCH_TOOL_KEYS` ([03_BACKEND.md](../implementation/Phase-01-Workbench/03_BACKEND.md) §2–3).
- [x] T6 — `services/workbench.py`: `get_workbench()` aggregation ([03_BACKEND.md](../implementation/Phase-01-Workbench/03_BACKEND.md) §2).
- [x] T7 — `api/routes/workbench.py` and `schemas/workbench.py`: `GET/PUT/POST /api/workbench*` ([06_API.md](../implementation/Phase-01-Workbench/06_API.md)).
- [x] T8 — `backend/tests/test_workbench.py` unit + integration tests ([07_TESTING.md](../implementation/Phase-01-Workbench/07_TESTING.md) §1). This checkpoint.

All four committed on branch `feature/t5-workbench-layout-service`, not yet pushed or merged — per the project owner's instruction, a PR is opened after this checkpoint and merge is held for explicit confirmation.

## Clarification recorded during this milestone

`03_BACKEND.md` §1 frames the Dashboard→Workbench move as a rename "in place" (`dashboard.py` → `workbench.py`). In practice this milestone added `backend/app/services/workbench.py`, `backend/app/schemas/workbench.py`, and `backend/app/api/routes/workbench.py` as **new** modules — `dashboard.py`/`routes/dashboard.py`/`/api/dashboard` are byte-for-byte untouched and stay mounted in `api_router` alongside the new `/api/workbench*` routes. This is required by `09_IMPLEMENTATION_TASKS.md` T14's own ordering note ("nothing deletes the fallback until Milestone 3's replacement is proven working") — the literal old-Dashboard removal is scheduled for T14 (Milestone 4), after the frontend actually renders Workbench. Treated as a clarification of already-locked spec text per ADR-0009 §2, not a scope change; recorded in `CURRENT_STATE.md`.

## Modified Files

**T5 (Layout persistence + tool catalog):**
- `backend/app/services/workbench.py` (new)

**T6 (Workbench aggregation):**
- `backend/app/services/workbench.py` (extended — `get_workbench()`, `serialize_layout()`)

**T7 (API routes + schemas):**
- `backend/app/schemas/workbench.py` (new)
- `backend/app/api/routes/workbench.py` (new)
- `backend/app/api/router.py` (`workbench.router` wired in, alongside `dashboard.router`)

**T8 (Backend tests):**
- `backend/tests/test_workbench.py` (new — 15 tests)
- `backend/pytest.ini` (`asyncio_mode = auto` added — first async test file in the suite)

**Tracking docs updated throughout:**
- `forge-docs/implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md`, `forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md`

## Current State

Milestone 2 (Backend) is fully done, committed locally on `feature/t5-workbench-layout-service` (not yet pushed/merged). Concretely, a fresh session can rely on:

- `GET /api/workbench`, `PUT /api/workbench/layout`, and `POST /api/workbench/layout/reset` all exist, are session-gated, and are fully functional against the real `workbench_layout` table (created by T3's migration).
- `GET /api/workbench` returns `{ layout: { panels, pinned_tools, tool_catalog }, data: { version, storage, recent_activity, recent_notes } }` — no `recent_secrets` field anywhere.
- `panels[].type` is **not** enum-validated (structural shape only: non-empty string `type`, boolean `visible`, no duplicate `type`) — an unregistered type like `"recent_projects"` is accepted and simply won't render until Phase 06 registers a matching frontend panel. This is tested at both the service and route level, since it's the exact mechanism ADR-0002/ADR-0005 depend on.
- `pinned_tools` keys **are** validated against `WORKBENCH_TOOL_KEYS` (11 entries — 9 available, 2 forward-looking: `prompt_studio`, `universal_converter`) — an unknown key is rejected with 422; a known-but-unavailable key is accepted (renders as "coming soon" once T10/T11 build the pin picker/panel).
- `/api/dashboard` (old route) and `GET /api/workbench` (new route) are both live simultaneously and independently tested — nothing about the old Dashboard changed this milestone.
- There is still no Workbench UI. The home page (`/`) is still the old Dashboard, unchanged. Milestone 3 builds the actual frontend against the now-complete `/api/workbench*` contract.
- Full backend pytest suite: 47/47 passing (32 pre-existing + 15 new), run twice consecutively to confirm the new test module's throwaway-data-dir approach is idempotent across repeated runs.

## Remaining Work

- **Milestone 3 — Frontend (T9–T12):** the generic runtime (`WorkbenchGrid`, `WorkbenchPanelCard`, `WorkbenchEmptyState`, `WorkbenchResetButton`, `WorkbenchCustomizeToggle`), `PinPickerDialog` (with disabled "coming soon" tiles for `prompt_studio`/`universal_converter`), the five active panels (this is where panels actually call `registerWorkbenchPanel` against T4's contract), and drag-and-drop + keyboard-only reordering plus every panel's empty/loading/error states.
- **Milestone 4 — Integration (T13–T16):** nav/palette rename to Workbench, old Dashboard removal (`dashboard.py`, `routes/dashboard.py`, `/api/dashboard`, `frontend/features/dashboard/`), manual verification, and the accessibility scan.

## Recommended Next Prompt

```
You are working in the Forge repository as a Claude Code session.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-01-Workbench/README.md
3. forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md
4. forge-docs/implementation/Phase-01-Workbench/IMPLEMENT.md
5. This checkpoint (forge-docs/history/2026-07-21-phase-01-milestone-2-backend.md)

Milestones 1 (Foundation, T1-T4) and 2 (Backend, T5-T8) are complete. Begin
work on: T9 in 09_IMPLEMENTATION_TASKS.md (the generic Workbench runtime --
WorkbenchGrid, WorkbenchPanelCard with an error boundary, WorkbenchEmptyState,
WorkbenchResetButton, WorkbenchCustomizeToggle, per 05_COMPONENTS.md §1.1),
the first task of Milestone 3 -- Frontend.

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly,
plus the milestone checkpoints in IMPLEMENT.md -- stop after T12 (end of
Milestone 3) even if the 10-12 task threshold hasn't been hit yet.

The specification is locked per forge-docs/decisions/0009-phase-specification-freeze.md.
Only bug fixes, clarifications, and typo corrections are in scope beyond the
documented tasks -- anything else (extra panels, workflows, a command palette,
a capability registry, a Projects interface, a plugin system, AI additions)
gets flagged and deferred, not built.

Note: /api/workbench* and /api/dashboard are both live right now (by design --
see this checkpoint's Clarification note); build T9-T12 against
/api/workbench*, and do not touch dashboard.py or /api/dashboard, that's T14.
```

## Known Risks

- **`WorkbenchLayoutUpdate.panels` is structurally validated only, on purpose.** Any future change that tries to "tighten" this into an enum on the backend would silently reintroduce the frontend/backend coupling ADR-0002 exists to remove — `test_workbench.py`'s unrecognized-panel-type tests are the guard against that regression.
- **`/api/dashboard` and `/api/workbench` both exist and will keep existing through Milestone 3.** Nothing currently prevents new frontend code from accidentally calling the old `/api/dashboard` instead of the new endpoint — worth double-checking during T9–T12 that all new Workbench frontend code targets `/api/workbench*` exclusively.
- **`backend/pytest.ini` now has `asyncio_mode = auto`**, added because `test_workbench.py` is the suite's first async test file. This affects the whole suite's async-test discovery going forward — harmless today since no other test file defines async tests, but worth remembering if a future test file adds async fixtures/tests of its own; they'll now be auto-detected without needing `@pytest.mark.asyncio`.
- **`test_workbench.py`'s integration tests share one module-scoped `TestClient` and are order-dependent** (the first test relies on no session existing yet; the rest rely on `/api/setup` having run). This mirrors the single-row, single-instance nature of `workbench_layout` itself, but it's a deliberate deviation from fully-independent test design — flagging so a future contributor doesn't "fix" the ordering dependency by parallelizing/reordering these tests without understanding why they're sequenced this way.
- **Known Issues carried over from Milestone 1** (T1's temporary `/api/vault` and `/vault` aliases) are unchanged by this milestone — still tracked in `CURRENT_STATE.md`.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-01-Workbench/CURRENT_STATE.md](../implementation/Phase-01-Workbench/CURRENT_STATE.md)
- [../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md](../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md)
- [2026-07-21-phase-01-milestone-1-foundation.md](2026-07-21-phase-01-milestone-1-foundation.md)
