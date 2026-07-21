# Checkpoint — Phase 01 Workbench — 2026-07-21

> **Trigger:** Milestone completion (Milestone 3 — Frontend, T9–T12)
> **Phase:** [Phase-01-Workbench](../implementation/Phase-01-Workbench/README.md)
> **Last Updated:** 2026-07-21

---

## Completed Tasks

- [x] T9 — The generic Workbench runtime ([05_COMPONENTS.md](../implementation/Phase-01-Workbench/05_COMPONENTS.md) §1.1).
- [x] T10 — `PinPickerDialog` ([05_COMPONENTS.md](../implementation/Phase-01-Workbench/05_COMPONENTS.md) §1.1, [02_UI.md](../implementation/Phase-01-Workbench/02_UI.md) §3.4).
- [x] T11 — The five active panels ([05_COMPONENTS.md](../implementation/Phase-01-Workbench/05_COMPONENTS.md) §1.2, [08_ACCEPTANCE.md](../implementation/Phase-01-Workbench/08_ACCEPTANCE.md) §6).
- [x] T12 — Drag/keyboard panel reorder, pin reorder, and every panel state ([02_UI.md](../implementation/Phase-01-Workbench/02_UI.md) §3.1–3.3). This checkpoint.

All four committed on branch `feature/t9-t12-workbench-frontend`, not yet pushed or merged — following the same PR-per-milestone pattern as Milestone 2 ([#10](https://github.com/DiegoDoug/forge/pull/10)); a PR is opened after this checkpoint and merge is held for explicit confirmation.

## Clarification recorded during this milestone

Continues the T5 clarification from Milestone 2: `01_SPEC.md`/`02_UI.md` describe Workbench as living at `/`. In practice the new frontend page was built at `frontend/app/(app)/workbench/page.tsx` — route `/workbench`, not `/` — because the old Dashboard page (`frontend/app/(app)/page.tsx`) must keep working until T14 explicitly removes it, per `09_IMPLEMENTATION_TASKS.md`'s own ordering note ("nothing deletes the fallback until Milestone 3's replacement is proven working") and T13's task description ("wire route `/` to the new Workbench page" — implying the page exists first, and the routing cutover is a distinct, later step). `/workbench` and `/` (old Dashboard) are both live and independently working right now. T13 does the actual cutover; T14 removes the old Dashboard and (per the note left in `CURRENT_STATE.md`'s "Next Claude Prompt") the `/workbench` staging route should be folded into that cutover rather than left dangling as a duplicate.

## Bug found and fixed during this milestone

`register-all.ts`'s bootstrap side-effect import (`import "@/features/workbench/register-all"`) was placed in `frontend/app/(app)/layout.tsx` — a Server Component — per what seemed like the natural reading of "imported once from the app shell" in `12_PANEL_INTERFACE.md` §4. Browser testing during T11 showed the Workbench page rendering the all-hidden empty state despite a fully-populated default layout from the backend: no panels were ever registered. Root cause: a side-effect-only import of client-only modules from a Server Component is not guaranteed to execute in the browser bundle in Next.js's App Router — nothing in the render tree actually instantiates a component from that import, so nothing forces it to load. Fixed by moving the import into `workbench-grid.tsx` (a Client Component that is actually rendered and that directly calls `getRegisteredPanels()`) — ES module evaluation order then guarantees registration completes before the registry is ever read, since it's a direct static import of the client module doing the consuming. Verified fixed via a fresh browser tab (to rule out stale console-log buffering, which briefly looked like the bug persisting after the fix).

## Modified Files

**T9 (Generic runtime):**
- `frontend/features/workbench/api.ts` (new)
- `frontend/features/workbench/components/{workbench-grid,workbench-panel-card,panel-error-boundary,workbench-empty-state,workbench-reset-button,workbench-customize-toggle}.tsx` (new)
- `frontend/app/(app)/workbench/page.tsx` (new)
- `frontend/app/(app)/layout.tsx` (register-all.ts import added, then reverted at T11 — see Bug above)
- `.claude/launch.json` (new, gitignored — local dev server config), `.gitignore` (`backend/.dev-data/` added)

**T10 (Pin picker):**
- `frontend/features/workbench/tool-metadata.ts` (new)
- `frontend/features/workbench/components/pin-picker-dialog.tsx` (new)
- `frontend/app/(app)/workbench/page.tsx` (customize-mode "Manage pinned tools" trigger added)

**T11 (Five panels):**
- `frontend/features/workbench/components/{pinned-tools-panel,recent-activity-panel,quick-actions-panel,system-status-panel}.tsx` (new)
- `frontend/features/notes/workbench-panel.tsx` (new)
- `frontend/features/workbench/register-all.ts` (five registrations wired in)
- `frontend/features/workbench/components/workbench-grid.tsx` (register-all.ts import moved here — the bug fix)
- `frontend/app/(app)/notes/page.tsx`, `frontend/app/(app)/secrets/page.tsx` (`?new=1` deep-link handling)

**T12 (Reorder):**
- `frontend/features/workbench/components/workbench-grid.tsx` (DndContext/SortableContext for panel reorder)
- `frontend/features/workbench/components/workbench-panel-card.tsx` (drag props typed against dnd-kit's real types)
- `frontend/features/workbench/components/pinned-tools-panel.tsx` (DndContext/SortableContext for pin reorder)

**Tracking docs updated throughout:**
- `forge-docs/implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md`, `forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md`

## Current State

Milestone 3 (Frontend) is fully done, committed locally on `feature/t9-t12-workbench-frontend` (not yet pushed/merged). Concretely, a fresh session can rely on:

- `/workbench` renders the full Workbench runtime against the real `/api/workbench*` backend: view mode (populated, all-hidden-empty, loading, error states), customize mode (per-panel show/hide, drag-and-drop + keyboard reorder, reset-to-default with confirmation), and the pin picker (pin/unpin, "coming soon" badges, drag-and-drop + keyboard reorder of pinned tiles).
- All five active panels are registered and rendering real data: Pinned Tools, Recent Activity, Quick Actions (with working deep-links into Notes/Secrets creation and Generators), Storage & System, Recent Notes.
- The old Dashboard (`/`, `frontend/features/dashboard/`, `/api/dashboard`) is completely untouched and still the live home page — nothing about it changed this milestone.
- Every empty/loading/error state specified in `02_UI.md` §3.1–3.2's tables has been live-verified against the real backend, not just read from source.
- Full validation clean: `tsc --noEmit`, `eslint .`, `next build`, and `docker compose build frontend` (the actual production Docker image, not just the local build) all succeed. No backend files were touched this milestone.

## Remaining Work

- **Milestone 4 — Integration (T13–T16):** sidebar/palette rename Dashboard → Workbench and the actual `/` route cutover (T13); removal of `frontend/features/dashboard/`, `backend/app/services/dashboard.py`, `backend/app/api/routes/dashboard.py`, and `/api/dashboard` (T14) — this is also where the `/workbench` staging route should be folded away, not left as a stray duplicate; a manual functional/performance/accessibility verification pass (T15); an automated accessibility scan plus a full `08_ACCEPTANCE.md` pass (T16).
- **Final Validation** against `08_ACCEPTANCE.md` follows T16 — this is the last milestone before the phase itself is done.

## Recommended Next Prompt

```
You are working in the Forge repository as a Claude Code session.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-01-Workbench/README.md
3. forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md
4. forge-docs/implementation/Phase-01-Workbench/IMPLEMENT.md
5. This checkpoint (forge-docs/history/2026-07-21-phase-01-milestone-3-frontend.md)

Milestones 1 (Foundation, T1-T4), 2 (Backend, T5-T8), and 3 (Frontend, T9-T12)
are complete. Begin work on: T13 in 09_IMPLEMENTATION_TASKS.md (sidebar and
command-palette entries rename Dashboard -> Workbench; wire route / to the
new Workbench page, per 02_UI.md §2), the first task of Milestone 4 --
Integration.

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly,
plus the milestone checkpoints in IMPLEMENT.md. This is the last milestone --
Final Validation against 08_ACCEPTANCE.md follows T16.

The specification is locked per forge-docs/decisions/0009-phase-specification-freeze.md.
Only bug fixes, clarifications, and typo corrections are in scope beyond the
documented tasks -- anything else (extra panels, workflows, a command palette,
a capability registry, a Projects interface, a plugin system, AI additions)
gets flagged and deferred, not built.

Note: the Workbench frontend page currently lives at /workbench, staged there
through Milestone 3 (see this checkpoint's Clarification note). T13 makes it
real at /; T14 removes the old Dashboard for real. Fold the /workbench
staging route into that cutover rather than leaving it dangling as a
duplicate once / renders Workbench directly.
```

## Known Risks

- **Keyboard-reorder verification used dispatched `KeyboardEvent`s, not the browser-automation tool's native key-press action**, because the latter didn't reliably deliver a `keydown` with the right `.code` to the focused element in this environment (confirmed by directly dispatching a real `KeyboardEvent` and observing `defaultPrevented: true` plus dnd-kit's `aria-describedby` wiring — the sensor itself works correctly). This is a testing-tool limitation noted for transparency, not a gap in the implementation, but worth a real manual keyboard test (a human at an actual keyboard) during T15's manual verification pass, since automated dispatch proves the sensor responds correctly but doesn't prove every real browser/OS combination's native Tab/Space/Arrow key delivery behaves identically.
- **`/workbench` is a genuinely new, permanent-feeling route that must not survive past T14.** If T13/T14 aren't executed carefully, `/workbench` could linger as a dead/duplicate route alongside the real `/` — flagged explicitly in the Next Prompt above so this doesn't get missed.
- **The already-running Docker Compose stack on this machine** (`forge-frontend-1`/`forge-backend-1`/`forge-nginx-1`, serving on port 8585) was left completely untouched — only `docker compose build frontend` (image build, no `up`) was run to verify buildability. A future session bringing that stack down and back up will pick up this milestone's frontend image automatically; that hasn't been done yet and wasn't required by this checkpoint.
- **Known Issues carried over from Milestones 1–2** (T1's temporary `/api/vault`/`/vault` aliases) are unchanged by this milestone — still tracked in `CURRENT_STATE.md`.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-01-Workbench/CURRENT_STATE.md](../implementation/Phase-01-Workbench/CURRENT_STATE.md)
- [../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md](../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md)
- [2026-07-21-phase-01-milestone-1-foundation.md](2026-07-21-phase-01-milestone-1-foundation.md)
- [2026-07-21-phase-01-milestone-2-backend.md](2026-07-21-phase-01-milestone-2-backend.md)
