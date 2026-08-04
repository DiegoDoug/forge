# Knowledge Hub — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04)
> **Status:** Confirmed — `01_SPEC.md` §7's four open questions resolved 2026-08-04; ready for implementation pending final review
> **Last Updated:** 2026-08-04

---

## 1. New or modified tables

Three new tables. **No existing table or column is modified.** Notes, Documents, Secrets, Tags, and Projects keep their current shape exactly.

### 1.1 `note_tag_links`

Mirrors the shipped `secret_tag_links` pattern in `models/secrets.py`.

| Column | Type | Notes |
|---|---|---|
| `note_id` | str | PK (composite), FK → `notes.id` |
| `tag_id` | str | PK (composite), FK → `tags.id` |

### 1.2 `document_tag_links`

| Column | Type | Notes |
|---|---|---|
| `document_id` | str | PK (composite), FK → `documents.id` |
| `tag_id` | str | PK (composite), FK → `tags.id` |

Both reference the **existing** `tags` table — one shared vocabulary across Secrets, Notes, and Documents, per `01_SPEC.md` §6.3. Neither table touches `secret_tag_links`.

### 1.3 `knowledge_links`

| Column | Type | Notes |
|---|---|---|
| `id` | str | PK, `new_id()` default |
| `source_type` | str | `"note"` or `"document"` |
| `source_id` | str | id of the source item (no FK — see §2) |
| `target_type` | str | `"note"` or `"document"` |
| `target_id` | str | id of the target item (no FK — see §2) |
| `created_at` | datetime | `utcnow()` default |

Indexes: `(source_type, source_id)` and `(target_type, target_id)` — both sides are queried, because a link is read from either end (`01_SPEC.md` FR15).

Uniqueness: the service enforces that a pair is stored once regardless of direction (FR18). A plain unique constraint on all four columns cannot express "A→B and B→A are the same link," so the service normalizes the pair before insert — ordering by `(type, id)` — and a unique constraint on the four normalized columns then holds. `04_DATABASE.md` §2 covers the residual risk.

## 2. Relationships and the one integrity trade-off

`note_tag_links` and `document_tag_links` are ordinary link tables with real foreign keys and full referential integrity.

`knowledge_links` is **polymorphic** — a single row may point at a `notes` row or a `documents` row — so SQLite cannot enforce a foreign key on `source_id` / `target_id`. This is a deliberate, recorded trade-off from `01_SPEC.md` §6.5:

- The alternative (four nullable FK columns: `source_note_id`, `source_document_id`, `target_note_id`, `target_document_id`, plus check constraints) preserves integrity but produces a table that is awkward to query from either side and needs a check constraint per combination.
- The chosen shape keeps queries simple and symmetric.

**Consequence:** deleting a Note or Document must delete its links in the service layer (`01_SPEC.md` FR17). This is not a database guarantee, so it is:

1. an explicit acceptance criterion (`08_ACCEPTANCE.md` AC17),
2. an explicit backend test (`07_TESTING.md` §1), and
3. called out here so nobody later assumes `ON DELETE CASCADE` is doing the work.

No other part of the Forge schema takes this trade-off. If a third linkable type ever appears, revisit.

## 3. Migration plan

Single Alembic migration: `backend/alembic/versions/0009_knowledge_hub.py`, following `0008_projects.py` as the immediate precedent.

- Revises `0008_projects`.
- Creates all three tables with `op.create_table`, using the guarded fresh-install/upgrade pattern every migration since `0006` uses (`04_DATABASE.md` conventions in Phase 06's equivalent doc).
- Creates the two `knowledge_links` indexes and the normalized unique constraint.
- **Purely additive.** No `ALTER TABLE` on any existing table, no data backfill, no destructive step.
- `downgrade()` drops the three tables in reverse dependency order. Because the migration is additive-only, downgrade is lossless with respect to pre-existing data — it discards only tag assignments and links created by this phase.
- No FTS5 changes. `notes_fts` and `documents_fts` and their triggers are untouched (`01_SPEC.md` §6.4).

## 4. Data lifecycle

- Tag assignments and links persist indefinitely, like the Notes/Documents/Secrets data they describe. No TTL, no scratch semantics.
- Deleting a Note or Document cascades to its tag links (real FK) and to its knowledge links (service-enforced, §2).
- Deleting a Tag removes its assignments across all three link tables. Tag deletion is an existing Secrets-side capability; this phase must ensure it does not leave dangling `note_tag_links` / `document_tag_links` rows — the FK makes this automatic if the existing delete path relies on the database, and must be verified either way (`07_TESTING.md` §1).
- Ingest artifacts remain outside the database entirely, unchanged (`01_SPEC.md` FR20).

## 5. Open items

None blocking. This schema is ratified by [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md) (Accepted 2026-08-04). The result cap is fixed at 100 (`01_SPEC.md` §6.6) — `updated_at` is already indexed on both `notes` and `documents`, so no additional index is needed to support the Hub's capped, sorted query.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [07_TESTING.md](07_TESTING.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/README.md](../../decisions/README.md)
