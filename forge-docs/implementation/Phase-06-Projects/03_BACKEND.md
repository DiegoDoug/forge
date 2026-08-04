# Projects — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Confirmed
> **Last Updated:** 2026-08-02

---

## 1. Service boundary

New `services/projects/` subpackage — `backend/app/services/projects/service.py`. Related existing backend code it touches: `backend/app/services/notes/service.py`, `backend/app/services/documents/service.py`, `backend/app/services/secrets/service.py` (each gains a `project_id` filter/field, not a rewrite), and `backend/app/services/model_playground/` (reused, not modified, for AI runs).

## 2. Business logic

`services/projects/service.py`:
- `list_projects(session, *, archived=False)` — same `archived` filter convention as Notes; returns projects with computed counts (a scalar subquery or a single `COUNT` per child table, run per-list-call — Forge's data volumes don't warrant a materialized counter column).
- `get_project(session, project_id)` — 404 via `NotFoundError` if missing, same as every other service.
- `create_project(session, data: ProjectCreateIn)`.
- `update_project(session, project_id, data: ProjectUpdateIn)` — `exclude_unset` partial update, same pattern as `notes.service.update_note`. Validates `default_provider`/`default_model` against `PROVIDER_REGISTRY` at the schema layer (see `06_API.md` §2), not here.
- `delete_project(session, project_id)`:
  1. For each of `Secret`, `Note`, `Document`, `PlaygroundRun`: select rows where `project_id` matches and clear it (ORM row updates within the same session/transaction — implementation detail; a raw bulk `UPDATE` would be an equally valid choice) — explicit unscoping per ADR-0014, done before the delete.
  2. Delete the `Project` row.
  3. Record one `activity.record(..., ActivityAction.deleted, "project", ...)` entry.
- `run_project_prompt(session, project_id, prompt: str)`:
  1. Load the project; 404 if missing.
  2. If `default_provider`/`default_model` unset, raise `AppError("Project has no default AI provider/model configured", status_code=400, code="project_ai_not_configured")`.
  3. Delegate directly to `app.services.model_playground.runs.create_run(session, prompt=prompt, targets=[RunTarget(provider=..., model=...)])` — Projects does not reimplement credential lookup, adapter dispatch, timeout, or error mapping.
  4. Stamp the resulting `PlaygroundRun.project_id = project_id` and re-commit (the run is already committed by `create_run`; this is a small follow-up update, mirroring how `runs.py` itself sets `r.run_id` post-hoc after the parent row exists).
  5. Record activity.
- `list_project_runs(session, project_id, *, limit=20)` — thin wrapper selecting `PlaygroundRun` where `project_id` matches, reusing the same `selectinload(PlaygroundRun.results)` query shape `runs.py` already uses (imported, not duplicated).

**Additions to existing services** (additive, non-breaking):
- `notes/service.py`: `list_notes(..., project_id: str | None = None)` adds `.where(Note.project_id == project_id)` when provided; `create_note`/`update_note` already pass through `data.model_dump()` / `exclude_unset` so no code change beyond the new optional schema field.
- `documents/service.py`: same treatment (`list_documents(..., project_id=None)`).
- `secrets/service.py`: same treatment alongside the existing `folder_id`/`tag_id` filters.

## 3. Integration with existing services

- `services/projects/service.py` imports `app.services.model_playground.runs` (for `create_run`/`RunTarget`) and `app.services.model_playground.providers` (for `PROVIDER_REGISTRY`, used by the schema validators in `06_API.md` §2) — this is the intended "Project → AI configuration → existing AI Provider Service" dependency chain from the mission brief, not a boundary violation: Model Playground's provider registry is the one canonical source of provider/model truth in the app, exactly as Secrets' `folder_id` filter doesn't duplicate anything either.
- No other feature imports from `services/projects/` in this phase (Secrets/Notes/Documents gain a plain nullable column and filter, not a dependency on the Projects service).

## 4. Architectural compliance

- [x] Routers stay thin — logic lives in `services/` (per `../../03_ARCHITECTURE.md` §2).
- [x] No cross-feature imports introduced beyond the explicitly-designed Projects → Model Playground dependency described above (which mirrors an existing, accepted pattern: Model Playground's own `runs.py` already depends on `providers/`).
- [x] No new external dependency — nothing to record in `06_TECH_STACK.md`.

## 5. TODO

None — this document is confirmed, not a template placeholder.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
