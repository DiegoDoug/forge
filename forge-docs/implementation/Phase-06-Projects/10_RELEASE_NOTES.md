# Projects — Release Notes

> **Purpose:** The release-facing summary of this phase — what shipped, what broke on purpose, what to do before upgrading. Not a duplicate of `CURRENT_STATE.md` (the day-to-day working log) or `POST_IMPLEMENTATION_REVIEW.md` (the retrospective) — this is the document a user or another engineer reads to understand what changed, not how it was built.
> **Scope:** This phase only.
> **Status:** Finalized — Released & Frozen. Tagged `v0.6.0-projects`, committed directly to `master`.
> **Version:** `v0.6.0-projects`
> **Last Updated:** 2026-08-03
> **Depends On:** [../../implementation/Phase-06-Projects/CURRENT_STATE.md](CURRENT_STATE.md), [../../implementation/Phase-06-Projects/08_ACCEPTANCE.md](08_ACCEPTANCE.md), [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)

---

## New Features

- A new **Projects** page (`/projects` list, `/projects/[id]` workspace), reachable from the sidebar and command palette, for grouping Secrets, Notes, and Documents into named workspaces.
- Every Secret, Note, and Document gains an optional project assignment — settable at creation and reassignable later (a form field on Secrets, a popover on each Notes card, a sidebar/toolbar picker on Documents), and every existing list view for the three gains an optional project filter. Unassigned items behave exactly as before Phase 06 — nothing about existing behavior changed.
- A project can declare a default AI provider/model, selected from the exact same provider catalogue Model Playground exposes. No new credential system: the project stores a provider key + model string only, never an API key.
- A project's workspace page can run a prompt against its configured default directly — this delegates entirely to Model Playground's existing run pipeline (same credential lookup, same adapters, same timeout/error handling), so the run shows up in both the project's own recent-activity list and Model Playground's run history, unified rather than duplicated.
- Deleting a project never destroys data: every Secret/Note/Document that referenced it is unassigned (`project_id` cleared), not deleted, and the delete confirmation dialog says so explicitly.
- A new "Recent Projects" Workbench panel (the concept named in [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) as Forge's eventual primary organizational unit).
- New backend: `services/projects/` (CRUD, counts, unscope-on-delete, AI-run delegation), 1 new table (`projects`), 7 new `/api/projects/*` endpoints, plus additive `project_id` columns and query-param filters on the existing Secrets/Notes/Documents/Model Playground endpoints.

## Breaking Changes

None. Every change to an existing table, schema, or endpoint is additive (a new nullable column, a new optional field, a new optional query parameter) — no existing request/response shape lost a field or changed meaning.

## Migrations

One new migration: `0008_projects.py`, creating `projects` and adding a nullable, indexed `project_id` to `secrets`, `notes`, `documents`, and `playground_runs`. Additive only. Verified live against both a fresh install (`SQLModel.metadata.create_all` path) and a simulated pre-existing database (explicit `op.create_table`/`op.add_column` path) — full upgrade → downgrade → upgrade cycle passes in both scenarios. The downgrade path required an explicit `op.batch_alter_table` fix (see Bug Fixes below) to correctly drop a column carrying a live foreign-key constraint on SQLite.

## Bug Fixes

Two real bugs were found during this phase's own manual QA and fixed before release (not deferred, not pre-existing):

- **`downgrade()` in `0008_projects.py` failed on SQLite when a `project_id` column carried a real foreign-key constraint** (the case on any fresh install, where `SQLModel.metadata.create_all` creates the FK from the start). A plain `op.drop_column` mis-recreated the table, leaving a stale FK reference. Fixed with an explicit `op.batch_alter_table` block, the documented-reliable way to drop an FK-bearing column on SQLite.
- **The new "Recent Projects" Workbench panel didn't appear**, even on a fresh install. Registering a panel on the frontend (`registerWorkbenchPanel`) alone isn't sufficient — it also has to be listed in the backend's `DEFAULT_LAYOUT_PANELS` (`app/services/workbench.py`), the same two-sided registration every prior panel (e.g. `recent_notes`) already required. Fixed by adding the entry; updated `test_workbench.py`'s hard-coded default-panel-count assertion (5 → 6) to match.

No fix was needed to already-shipped functionality outside this phase — the full pre-existing backend test suite passes unchanged, and Secrets/Notes/Documents/Model Playground/Workbench all continue to build and behave identically for anything not touched by this phase's additive changes.

## Known Issues

None outstanding. A third, smaller UI issue (Base UI's `Select` component rendering a raw item value instead of its label in the two new pickers this phase introduced) was found and fixed in the same session — see `POST_IMPLEMENTATION_REVIEW.md` "Unexpected Problems" for detail; it doesn't warrant its own QA ticket since it was fully resolved and re-verified live before release.

## Upgrade Notes

A normal restart picks up the change: the new migration applies automatically on backend startup, no manual step, no data backfill, no new required environment variables. Projects is fully opt-in — with zero projects created, Secrets/Notes/Documents behave exactly as before, and the "Recent Projects" Workbench panel shows an empty state with a create action. Operators who already customized their Workbench layout before this release won't see the new panel automatically (per the existing panel system's design — a registered panel not yet in a saved layout doesn't retroactively appear); use "Reset to default" in Workbench customize mode to pick it up. There is no way to add a single new panel individually without a full reset — a pre-existing Workbench (Phase 01) characteristic, not something this phase changed.

## Deferred Work

- **Multi-project membership per entity** — an entity belonging to more than one project. Evaluated and explicitly deferred in [ADR-0014](../../decisions/0014-project-data-model-shape.md) §3; would need a join table and its own ADR if real demand shows up.
- **Nested/sub-projects, per-project access control/sharing** — out of scope per `01_SPEC.md` §5; Forge remains single-tenant.
- **Deep AI-assisted editing inside Notes/Documents** — a candidate for Knowledge Hub (Phase 07) or later, not this phase.
- **Prompt Studio scoping into Projects** — named as a future candidate in ADR-0005, not implemented here.

## Cross-references

- [../../implementation/Phase-06-Projects/CURRENT_STATE.md](CURRENT_STATE.md)
- [../../implementation/Phase-06-Projects/08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../implementation/Phase-06-Projects/09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)
- [../../decisions/0005-projects-primary-organizational-unit.md](../../decisions/0005-projects-primary-organizational-unit.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
