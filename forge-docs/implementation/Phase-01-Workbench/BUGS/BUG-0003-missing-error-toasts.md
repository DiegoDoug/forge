# BUG-0003 — 3 of 4 layout-mutation failure paths show no error toast

> **Classification:** 🟡 MAJOR — significant UX inconsistency, per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §2 — **project owner to decide fix-now vs. backlog**
> **Status:** Open — awaiting project-owner decision
> **Found:** Post-T16 independent code-review audit, 2026-07-21
> **Files:** `frontend/features/workbench/components/workbench-grid.tsx` (`handleVisibilityChange`, `handleDragEnd`), `frontend/features/workbench/components/pinned-tools-panel.tsx` (`handleDragEnd`)

---

## The issue

Four places call `useUpdateLayoutMutation()`'s `mutate(...)`:

1. `PinPickerDialog.togglePin` — passes `{ onError: () => toast.error("Couldn't update pinned tools. Try again.") }`.
2. `WorkbenchGrid.handleVisibilityChange` — no second argument, no toast.
3. `WorkbenchGrid.handleDragEnd` (panel reorder) — no second argument, no toast.
4. `PinnedToolsPanel.handleDragEnd` (pin reorder) — no second argument, no toast.

The mutation hook's built-in `onError` (in `frontend/features/workbench/api.ts`) always rolls back the optimistic cache update regardless — so the *data* is never wrong. But for 3 of the 4 actions, a failed save reverts silently with zero user-facing explanation: a panel drag, a visibility toggle, or a pin drag can appear to just snap back for no visible reason.

## Why this is MAJOR, not a BLOCKER

No data loss (the rollback is correct), no crash, no security issue. But `02_UI.md` §3.4 and `08_ACCEPTANCE.md`'s UX criteria describe "roll back optimistically with a toast" as the expected failure behavior for layout-mutating actions generally, and 3 of 4 call sites don't do the second half of that. This is a real, user-visible inconsistency worth an explicit call, not a MINOR cleanup item.

## Recommended fix (if the project owner picks this up)

Add the same `{ onError: () => toast.error(...) }` second argument to the three call sites listed above, with wording appropriate to each action (e.g. "Couldn't reorder panels. Try again.", "Couldn't update panel visibility. Try again.", "Couldn't reorder pinned tools. Try again.").

## Cross-references

- [../02_UI.md](../02_UI.md) §3.4
- [../08_ACCEPTANCE.md](../08_ACCEPTANCE.md) §2
- [../CURRENT_STATE.md](../CURRENT_STATE.md)
