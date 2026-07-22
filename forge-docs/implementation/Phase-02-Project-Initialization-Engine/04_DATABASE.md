# Project Initialization Engine — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted.
> **Last Updated:** 2026-07-22

---

## 1. New or modified tables

One new table: `project_init_generations`, backing model `ProjectInitGeneration` (`backend/app/models/project_init.py`).

| Column | Type | Notes |
|---|---|---|
| `id` | `str` (UUID, primary key) | matches `models/base.py` convention used by `Note`, etc. |
| `kind` | `str` | `"fdk_phase"` or `"ai_instructions"` — plain string column (not a DB enum) for forward compatibility if a third kind is added later, validated at the Pydantic layer instead. |
| `name` | `str` | short display name: phase name (fdk_phase) or project name (ai_instructions). |
| `config` | `JSON` (SQLite JSON1 via SQLAlchemy `JSON` type) | the full validated input payload — the source of truth re-rendered on every download. |
| `created_at` | `datetime` | via `models/base.py` `utcnow` default, matching every other model. |

No `updated_at` — generation history records are immutable once created (only created or deleted, never edited).

## 2. Relationships

None. This table has no foreign keys to any existing table (Vault/Secrets, Notes, Documents) and nothing references it — it is a standalone log of past generations, conceptually closer to `ActivityLog` than to a content-owning table, except it additionally stores the config needed for re-download.

## 3. Migration plan

One explicit Alembic migration, `0004_project_init.py`, additive only:

```sql
CREATE TABLE project_init_generations (
    id VARCHAR NOT NULL PRIMARY KEY,
    kind VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    config JSON NOT NULL,
    created_at DATETIME NOT NULL
);
CREATE INDEX ix_project_init_generations_created_at ON project_init_generations (created_at);
```

No changes to any existing table. No data migration/backfill needed (new table starts empty).

## 4. Data lifecycle

Persists indefinitely, like Vault/Notes — this is user-meaningful history (past project scaffolds a developer may want to revisit), not scratch data with TTL cleanup (unlike Ingest's upload scratch space). Capped for *display* at 20 most-recent rows (`list_history(limit=20)`, [03_BACKEND.md](03_BACKEND.md) §2) but not capped at the storage layer — old rows are only removed by explicit user delete. Given expected volume (a developer generating project scaffolds is an occasional action, not a high-frequency one), unbounded storage growth is not a realistic concern for a single-tenant SQLite deployment; revisit only if usage patterns prove otherwise.

## 5. TODO

None.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/README.md](../../decisions/README.md)
