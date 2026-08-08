# Frontend Reimagine — Database

> **Purpose:** State this phase's database impact.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved 2026-08-06; holds as implemented — zero schema/migration diff confirmed throughout and re-verified at RC 2026-08-07.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [03_BACKEND.md](03_BACKEND.md)

---

## 1. Database impact: none

**No table, column, index, constraint, or migration is added, altered, or removed by this phase.**

Phase 09 changes how existing data is presented. It does not change what data exists, how it is shaped, or how it is stored. No Alembic migration is required or permitted.

## 2. Persisted state this phase reads but does not change

Three pieces of user state are persisted server-side and consumed by surfaces this phase redesigns. All three keep their storage, their shape, and their semantics:

| State | Storage | Consumed by | Phase 09 |
|---|---|---|---|
| Workbench layout — panel order, panel visibility, pinned tools | `workbench` service | `/` | Presentation only. The optimistic-update contract, including preservation of unregistered panel types, is preserved exactly. |
| Theme preference | `settings` service, via `settingsApi.updateTheme` | `/settings`, `ThemeProvider` | Presentation only. Local `next-themes` behavior and server sync both unchanged. |
| Project scoping (`project_id` foreign keys on secrets/notes/documents/runs) | Per [ADR-0014](../../decisions/0014-project-data-model-shape.md) | Every project-scoped surface | Presentation only. Unscope-on-delete semantics unchanged. |

## 3. Verification

The backend test suite must be green and **unchanged** at phase end. A modified backend test on this phase's branch indicates backend behavior was altered, which is out of contract — see [`03_BACKEND.md`](03_BACKEND.md) §4.

## 4. Cross-references

- [03_BACKEND.md](03_BACKEND.md) · [01_SPEC.md](01_SPEC.md) §5 · [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
- [../../../docs/Database.md](../../../docs/Database.md)
