# Projects — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Confirmed — see ADR-0014 for the decision rationale
> **Last Updated:** 2026-08-02

---

## 1. New or modified tables

**New table: `projects`**

| Column | Type | Notes |
|---|---|---|
| `id` | `str` (pk) | `new_id()`, same convention as every other table |
| `name` | `str(200)` | required, indexed |
| `description` | `str(2000)` | default `""` |
| `color` | `str(20)` | default `"#6366f1"` (same default as `Tag.color`) |
| `archived` | `bool` | default `False`, indexed |
| `default_provider` | `str(50) \| None` | nullable; a `PROVIDER_REGISTRY` key, not a FK |
| `default_model` | `str(100) \| None` | nullable; a model string within that provider's catalogue |
| `created_at` | `datetime` | `utcnow()` |
| `updated_at` | `datetime` | `utcnow()`, updated on every edit |

**Modified tables** — one additive nullable indexed column each, no other changes:

| Table | New column |
|---|---|
| `secrets` | `project_id: str \| None` (FK `projects.id`, indexed) |
| `notes` | `project_id: str \| None` (FK `projects.id`, indexed) |
| `documents` | `project_id: str \| None` (FK `projects.id`, indexed) |
| `playground_runs` | `project_id: str \| None` (FK `projects.id`, indexed) |

## 2. Relationships

- `Project` is the parent side of four independent nullable one-to-many relationships (Secret, Note, Document, PlaygroundRun each optionally belong to one Project). No `Relationship()` back-reference is required on `Project` for the initial cut — the four child tables are queried by `project_id` filter (same pattern as `Secret.folder_id`), not via SQLAlchemy relationship traversal, to avoid coupling `Project`'s model module to every other feature's model module (`models/project.py` must not import `models/secrets.py`, `models/note.py`, etc. — see `07_CODING_STANDARDS.md` §1 "features don't import from each other," which extends to backend models by the same spirit even though it's phrased for frontend features).
- No FK is declared with a DB-level `ON DELETE` action (SQLite's FK enforcement is off by default in this codebase, consistent with existing `folder_id`/`run_id` FKs). Unscoping on project delete is done explicitly in `services/projects/service.py` (see `03_BACKEND.md` §2).

## 3. Migration plan

One new Alembic migration: `backend/alembic/versions/0008_projects.py`, `down_revision = "0007"`.

`upgrade()`:
1. Create `projects` table with the columns above, `ix_projects_name` and `ix_projects_archived` indexes — guarded by `if "projects" not in inspector.get_table_names()` (same pattern as `0006_model_playground.py`, since `SQLModel.metadata.create_all()` on a fresh install already creates it once `models/project.py` is registered in `models/__init__.py`).
2. Add nullable `project_id` column + index to `secrets`, `notes`, `documents`, `playground_runs` via `op.add_column` / `op.create_index`, each guarded by a column-existence check (`inspector.get_columns(table)`) for the same fresh-install-vs-upgrade reason.

`downgrade()`: drop the four `project_id` indexes/columns (reverse order), then drop `ix_projects_archived`, `ix_projects_name`, and the `projects` table.

This is a straightforward additive migration — no column type changes, no data migration/backfill needed (new columns start `NULL` for all existing rows), no risk to existing data.

## 4. Data lifecycle

Persists indefinitely, like Vault/Notes/Documents (not scratch data — no TTL cleanup, unlike Ingest). A Project is deleted only by explicit user action; deleting it unscopes (never deletes) its children, per ADR-0014 §2.

## 5. TODO

None — this document is confirmed, not a template placeholder.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
