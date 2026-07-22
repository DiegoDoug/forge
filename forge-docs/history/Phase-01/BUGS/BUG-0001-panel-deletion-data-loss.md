# BUG-0001 — Panel drag-reorder/visibility-toggle silently deletes unregistered panel types

> **Classification:** 🔴 BLOCKER — data loss, per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §2
> **Status:** ✅ Fixed and verified
> **Found:** Post-T16 independent code-review audit, 2026-07-21
> **Fixed:** Same day
> **File:** `frontend/features/workbench/components/workbench-grid.tsx`

---

## The bug

`WorkbenchGrid` computed `savedPanels` as `data.layout.panels` filtered to only registry-known types (line 103), then built the `PUT /api/workbench/layout` payload for **both** `handleVisibilityChange` and `handleDragEnd` from that pre-filtered list, not the original unfiltered `data.layout.panels`.

Concretely: if a user's persisted layout contained an entry with a `type` the currently-running frontend build doesn't register (e.g. `recent_projects` before Phase 06 registers it, or any panel type from a version mismatch, or a panel later removed), that entry would be **silently and permanently deleted** from the layout the next time the user reordered any panel or toggled any panel's visibility — not un-hidden, not renamed, gone from storage entirely.

This directly contradicted `12_PANEL_INTERFACE.md` §3 item 6's stated guarantee: an unregistered panel type must be "safely inert" until a matching panel is registered. "Safely inert" was implemented as "gets deleted from storage the moment the user does anything unrelated to it."

## Why this is a BLOCKER

Persistent, predictable layout state is one of Workbench's core promises (`01_SPEC.md` §2's user stories, FR7). A user action causing unrelated saved state to silently disappear is exactly the "data loss" criterion in `12_BUG_CLASSIFICATION.md` §2 — not technical debt, not a UX nit.

## The fix

Both handlers now build their mutation payload from the full, unfiltered `data.layout.panels`:

- `handleVisibilityChange`: maps over the full list, only touching the entry whose `type` matches — any other entry (registered or not) passes through unchanged.
- `handleDragEnd`: computes the new order among registered panels only (`arrayMove(savedPanels, ...)`), then walks the full original list and re-inserts the reordered registered entries back into their original slots, leaving any unregistered entry exactly where it was, untouched.

`savedPanels` is still used for *rendering* (only registered panels should ever render) — the bug was specifically that the rendering-filtered list leaked into the *persistence* payload. That's now a strict separation.

## Verification

- `tsc --noEmit`, `eslint .`, `next build` all clean.
- Live regression test against a fresh backend instance: seeded a layout via direct `PUT` with `recent_projects` (unregistered) placed between two registered panels, then via the real UI — customize mode, real visibility toggle, then a real keyboard-driven drag-reorder — confirmed via `GET /api/workbench` after each action that `recent_projects` survived, unchanged, in its original relative position, while the registered panels correctly toggled/reordered around it.

## Cross-references

- [../../../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../../../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §3 item 6
- [../../../decisions/0002-workbench-panel-architecture.md](../../../decisions/0002-workbench-panel-architecture.md)
- [../../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../../implementation/Phase-01-Workbench/CURRENT_STATE.md)
- [../POST_IMPLEMENTATION_REVIEW.md](../POST_IMPLEMENTATION_REVIEW.md)
