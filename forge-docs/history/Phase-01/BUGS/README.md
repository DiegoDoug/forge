# Workbench — Bugs

> **Purpose:** Tracks issues found during or after implementation, classified per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md). All five here came from the same source: an independent, adversarial code-review audit performed after T16's Final Validation, requested specifically to find what functional/automated verification couldn't.
> **Scope:** This phase only.

---

| Issue | Classification | Status |
|---|---|---|
| [BUG-0001](BUG-0001-panel-deletion-data-loss.md) — Panel reorder/toggle silently deletes unregistered panel types | 🔴 BLOCKER | ✅ Fixed and verified |
| [BUG-0002](BUG-0002-pinned-tools-duplicate-validation.md) — No duplicate-key validation on `pinned_tools` | 🟢 MINOR | Open — backlog |
| [BUG-0003](BUG-0003-missing-error-toasts.md) — 3 of 4 layout-mutation failure paths show no error toast | 🟡 MAJOR | Open — awaiting project-owner decision |
| [BUG-0004](BUG-0004-dead-recent-notes-computation.md) — `get_workbench()` computes `recent_notes` that nothing consumes | 🟢 MINOR | Open — backlog |
| [BUG-0005](BUG-0005-unused-onerror-prop.md) — `onError` panel-contract prop never called by any shipped panel | 🟢 MINOR | Open — backlog |

Per the project owner's ruling: BUG-0001 blocked the RC1→RC2 transition and is now fixed. The remaining four do not block merge — BUG-0003 (MAJOR) needs an explicit project-owner decision at some point, but that decision itself doesn't gate this phase closing; BUG-0002/0004/0005 (MINOR) ship as backlog, full stop.
