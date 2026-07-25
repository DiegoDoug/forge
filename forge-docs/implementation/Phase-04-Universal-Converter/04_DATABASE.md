# Universal Converter — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — filled in against [`01_SPEC.md`](01_SPEC.md) v0.2.0, pending owner review.
> **Last Updated:** 2026-07-23

---

## 1. New or modified tables

**None.** This phase introduces zero SQLModel tables and modifies zero existing ones. Confirmed with the project owner during specification (2026-07-23) as one of the four scope decisions in [`01_SPEC.md`](01_SPEC.md) §1 — file-based conversion keeps Ingest's existing ephemeral model exactly as it is today, and no conversion-history/presets persistence is added.

## 2. Relationships

Not applicable — no new tables means no new foreign keys or relationships.

## 3. Migration plan

**No Alembic migration is required for this phase.** Stating this explicitly per this document's own template instruction ("if this phase introduces no schema changes, state that explicitly rather than leaving this file as an unfilled template").

## 4. Data lifecycle

Unchanged from today:

- **Text & Data conversions** (JSON/YAML/XML/CSV/regex/URL/Unicode/cron/timestamp/diff): stateless — input and output live only in React component state in the browser, never sent to or stored by the backend (except cron's expression, which is computed and returned, never persisted).
- **Documents conversions** (the wrapped Ingest pipeline): scratch data only — `Job`/`FileTask` records live in the in-memory `JobStore` (`backend/app/services/ingest/jobs.py`), uploaded/converted files live under `ingest_jobs_dir` on disk, and both are deleted by the existing TTL cleanup thread (`ingest_job_ttl_minutes`, default 120 minutes) or immediately after a successful conversion reads the upload (`task.upload_path.unlink` in `converter.py`). None of this changes — the new `MarkItDownProvider` adapter (see [`03_BACKEND.md`](03_BACKEND.md) §2) delegates to the exact same `JobStore` and cleanup thread, not a new one.
- The only persistence this phase's file-conversion path touches at all is the existing `ActivityLog` write (`activity.record(..., ActivityAction.converted, ...)` in `api/routes/ingest.py`), which is unmodified.

## 5. TODO

- [ ] Project-owner confirmation that "no persistence" remains correct if a future fast-follow adds a second provider — flagged here so a later phase revisits this file rather than assuming it forever, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md)'s "Frozen" discipline once this phase ships.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/README.md](../../decisions/README.md)
