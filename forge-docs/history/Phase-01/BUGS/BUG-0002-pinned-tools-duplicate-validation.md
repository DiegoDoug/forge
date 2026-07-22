# BUG-0002 — No duplicate-key validation on `pinned_tools`

> **Classification:** 🟢 MINOR — validation completeness / cleanup, per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §2
> **Status:** Open — backlogged, not fixed in Phase 01
> **Found:** Post-T16 independent code-review audit, 2026-07-21
> **File:** `backend/app/services/workbench.py` (`_validate_pinned_tools`, adjacent to `_validate_panels`)

---

## The issue

`_validate_panels` explicitly rejects a `panels` list containing a duplicate `type`. `_validate_pinned_tools`, three lines below it in the same file, only checks that each key exists in `WORKBENCH_TOOL_KEYS` — it never checks for duplicates within the list itself. A `PUT /api/workbench/layout` with `{"pinned_tools": ["secrets", "secrets"]}` is accepted and persisted verbatim.

## Why this is MINOR, not a BLOCKER

- Not reachable through the normal UI: `PinPickerDialog`'s toggle logic (add-if-absent, remove-if-present) cannot produce a duplicate on its own.
- No data loss or corruption — the duplicate is just stored as given.
- If it were ever reached (a hand-crafted API call, or a future UI bug), the practical symptom is a React key collision / undefined dnd-kit sortable behavior in `PinnedToolsPanel` — a rendering glitch, not a crash or lost data.

## Recommended fix (when picked up)

Add a duplicate check to `_validate_pinned_tools` mirroring `_validate_panels`'s existing `seen: set[str]` pattern — a few lines, no schema change needed.

## Cross-references

- [../../../../backend/app/services/workbench.py](../../../../backend/app/services/workbench.py)
- [../../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../../implementation/Phase-01-Workbench/CURRENT_STATE.md)
