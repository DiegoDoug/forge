# BUG-0005 — `onError` panel-contract prop is never called by any shipped panel

> **Classification:** 🟢 MINOR — cleanup / unused interface surface, per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §2
> **Status:** Open — backlogged, not fixed in Phase 01
> **Found:** Post-T16 independent code-review audit, 2026-07-21
> **Files:** `frontend/features/workbench/panel-types.ts` (`WorkbenchPanelProps.onError`), `frontend/features/workbench/components/workbench-panel-card.tsx` (`manualError` state + `PanelErrorFallback` branch)

---

## The issue

`WorkbenchPanelProps` gives every panel an `onError: (error: unknown) => void` callback so a panel can proactively signal "I failed" without throwing. None of the five shipped panels (`PinnedToolsPanel`, `RecentActivityPanel`, `QuickActionsPanel`, `SystemStatusPanel`, `RecentNotesPanel`) destructure or call it — each handles its own `isError` state with inline retry UI instead. The corresponding `manualError` state and `PanelErrorFallback` branch in `WorkbenchPanelCard` therefore has zero live invocation anywhere in the codebase, and (since no frontend test runner exists per `07_TESTING.md` §2) zero test coverage either.

## Why this is MINOR, not a bug

`12_PANEL_INTERFACE.md` §3 item 4 says a panel "can" call `onError`, not "must" — this is optional, forward-looking infrastructure, not a broken contract. It's flagged here purely as an accuracy note: the error-containment story in the panel interface doc reads as having two mechanisms (thrown-error boundary, proactive `onError`), and only the first has ever been exercised by real code, and even that one only by a genuinely thrown render exception, which no current panel produces either.

## Recommended action (when picked up)

Either exercise this path deliberately once (e.g. have one panel call `onError` for a genuinely unrecoverable state, to prove the mechanism works end-to-end) or, if no Phase 01/02 panel ever needs it, note in `12_PANEL_INTERFACE.md` that this is speculative infrastructure pending a real consumer, so a future reader doesn't assume it's been verified.

## Cross-references

- [../../../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../../../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §3 item 4
- [../../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../../implementation/Phase-01-Workbench/CURRENT_STATE.md)
