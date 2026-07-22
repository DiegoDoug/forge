# BUG-0004 — `get_workbench()` computes `recent_notes` that nothing consumes

> **Classification:** 🟢 MINOR — performance / dead code, per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §2
> **Status:** Open — backlogged, not fixed in Phase 01
> **Found:** Post-T16 independent code-review audit, 2026-07-21
> **Files:** `backend/app/services/workbench.py` (`get_workbench`), `backend/app/schemas/workbench.py` (`WorkbenchData.recent_notes`), `frontend/features/notes/workbench-panel.tsx` (`RecentNotesPanel`)

---

## The issue

Every `GET /api/workbench` runs a real SQL query (`select(Note)...limit(6)`) and serializes the result into `WorkbenchData.recent_notes`. `RecentNotesPanel` — the only panel that could plausibly use it — deliberately fetches its own data independently via the Notes feature's own `useNotes()` hook instead (a legitimate, spec-consistent choice per `12_PANEL_INTERFACE.md`'s "each panel owns its own data fetching" principle). `data.data.recent_notes` from `useWorkbenchQuery()` is never read anywhere in `frontend/features/workbench/` or `frontend/features/notes/`.

This differs from the other two `WorkbenchData` fields: `storage`/`version` is genuinely read by `SystemStatusPanel`, and `recent_activity` is genuinely read by `RecentActivityPanel`. `recent_notes` is the odd one out — likely a leftover from before `RecentNotesPanel`'s data-ownership decision was made at T11, never cleaned up afterward.

## Why this is MINOR, not a BLOCKER or MAJOR

No functional impact — nothing is wrong for a user. It's wasted backend work (one extra query + payload bytes on the single hottest endpoint in the feature) and a documentation/architecture inconsistency, not a defect anyone experiences.

## Recommended fix (when picked up)

Remove `recent_notes` from `get_workbench()`'s query and return value, from `WorkbenchData`/`WorkbenchOut` (backend schema), and from the corresponding frontend `WorkbenchData` interface in `api.ts`. Update `docs/API.md`'s `/api/workbench` description accordingly.

## Cross-references

- [../../../../backend/app/services/workbench.py](../../../../backend/app/services/workbench.py)
- [../12_PANEL_INTERFACE.md](../12_PANEL_INTERFACE.md)
- [../CURRENT_STATE.md](../CURRENT_STATE.md)
