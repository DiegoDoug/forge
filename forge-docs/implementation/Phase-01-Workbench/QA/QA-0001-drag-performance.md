# QA-0001 — Verify Workbench drag performance

> **Purpose:** Close out the one performance criterion in [`../08_ACCEPTANCE.md`](../08_ACCEPTANCE.md) §4 that T16 could not measure.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual Browser Session (not automatable in this repo's current toolchain — no frontend test runner exists per [`../07_TESTING.md`](../07_TESTING.md) §2)
> **Blocks Phase 01 sign-off:** No — tracked here specifically so it does not block. See [`../08_ACCEPTANCE.md`](../08_ACCEPTANCE.md) §4 and [`../CURRENT_STATE.md`](../CURRENT_STATE.md) for why.

---

## Why this is a QA task, not an implementation task

T16's automated browser session could not produce a reading for this criterion for a reason specific to that session, not to the app: the session's browser tab did not service animation frames at all — confirmed directly (`element.getAnimations()[0].currentTime` stayed at exactly `0` across 3+ real elapsed seconds, and a `requestAnimationFrame` callback scheduled directly never fired). No FPS number taken under those conditions would mean anything. This needs a real browser tab on a real device, which is a QA/manual-session activity, not something to keep re-attempting with the same automated tool.

## Scope

Drag-and-drop panel reordering and pinned-tool reordering in Workbench customize mode (`/`, "Customize" → drag a panel or a pinned tool). Both use `@dnd-kit/core`'s `PointerSensor` with CSS-transform-based dragging (`frontend/features/workbench/components/workbench-grid.tsx`, `frontend/features/workbench/components/pinned-tools-panel.tsx`) — not layout-triggering property changes, which is the right approach for 60fps, but that's a code-review inference, not a measurement.

## Acceptance criteria (from `08_ACCEPTANCE.md` §4)

- [ ] **60 FPS**, no visible jank, during a panel drag-reorder and a pinned-tool drag-reorder. Measure via browser devtools' Performance panel or an FPS meter, per [`../07_TESTING.md`](../07_TESTING.md) §3.
- [ ] **React DevTools Profiler**: during a drag interaction, only the dragged panel/tile and its immediate neighbors re-render — not the full grid, not unrelated panels' own data-fetching hooks re-firing.
- [ ] **No unnecessary re-renders** more broadly: toggling a panel's visibility or reordering pins shouldn't cause sibling panels to refetch or re-render.

## How to run it

1. Open the app in a real Chrome/Firefox/Safari tab (not an automation-driven one) with React DevTools installed.
2. Enter customize mode on `/`.
3. Open devtools' Performance panel, start recording, drag a panel to a new position, stop recording. Inspect the frame rate during the drag.
4. Repeat for a pinned-tool drag inside the Pinned Tools panel.
5. Switch to the React DevTools Profiler tab, start profiling, repeat both drags, stop profiling. Inspect the flame graph for which components actually re-rendered.

## Result

_Not yet run. Fill in with actual numbers/screenshots and a pass/fail once done._

## Cross-references

- [../08_ACCEPTANCE.md](../08_ACCEPTANCE.md) §4
- [../07_TESTING.md](../07_TESTING.md) §3
- [../CURRENT_STATE.md](../CURRENT_STATE.md)
