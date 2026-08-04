# Projects — Current State

> **Purpose:** Live snapshot of where this phase actually stands, updated at every checkpoint.
> **Scope:** This phase only — updated continuously, never left stale.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** COMPLETE / READY FOR RELEASE
> **Last Updated:** 2026-08-03

---


## Current Status

Phase 06 is complete. All backend and frontend work is implemented, tested, manually QA'd in a real browser, security-reviewed, and documented. Full regression suite (backend + frontend) passes with zero failures. No known blocking issues remain.

## Completed

- [x] Specification: `01_SPEC.md`, `08_ACCEPTANCE.md`, and all supporting docs (`02_UI.md`–`07_TESTING.md`, `09_IMPLEMENTATION_TASKS.md`) written and confirmed.
- [x] [ADR-0014](../../decisions/0014-project-data-model-shape.md) (Project data model shape) drafted and accepted; `03_ARCHITECTURE.md` §4 updated.
- [x] Backend: `Project` model, migration `0008_projects.py`, `schemas/projects.py`, `services/projects/service.py`, `api/routes/projects.py`; additive `project_id` scoping on Secrets/Notes/Documents/Model Playground runs.
- [x] Backend tests: `test_projects_service.py`, `test_projects_api.py`, `test_projects_migration.py` (upgrade/downgrade/upgrade cycle verified against both a fresh install and a simulated pre-existing database) — 22 new tests, all passing.
- [x] Frontend: `features/projects/` (api.ts, picker, form/delete dialogs, card, AI config, AI quick-run, Workbench panel), `/projects` and `/projects/[id]` pages, nav entry, command palette entry (automatic via nav registry).
- [x] Cross-feature integration: project picker/filter wired into Secrets, Notes (via a popover on the note card), and Documents (sidebar filter + editor toolbar).
- [x] Full regression pass: backend test suite (all tests, not just new ones) green; frontend `tsc --noEmit`, `eslint`, and `next build` all clean.
- [x] Manual browser QA: full workflow exercised live (create/edit/archive/delete a project, assign/unassign a secret/note/document, configure a default AI provider/model, run a real prompt end-to-end against OpenAI with a test credential — verified provider error handling on an intentionally invalid key, run appeared in both the project's and Model Playground's history, deletion verified to unscope rather than destroy data via direct API checks, Workbench panel empty/populated states, command palette, dark mode, mobile viewport).
- [x] Two real bugs found and fixed during QA (see Known Issues below for detail — both resolved, not deferred).
- [x] Security review completed (see Known Issues — no findings).
- [x] Documentation: `docs/API.md`, `docs/Database.md`, `docs/Security.md` updated; `02_ROADMAP.md` status row updated; this phase's own docs finalized.

## In Progress

- [ ] None — phase complete.

## Remaining

- [ ] None.

## Known Issues

None outstanding. Two issues were found and fixed during this session's QA pass (not deferred):

- Base UI's `Select.Value` renders the raw item `value`, not its label, unless given a render function — `ProjectPicker` and the AI provider picker initially showed raw values (`__none__`, `openai`) instead of human labels. Fixed by passing a children-as-function to `SelectValue` in both components (`features/projects/project-picker.tsx`, `features/projects/project-ai-config.tsx`). Scoped to the two new components Projects owns; the pre-existing shared `Select` wrapper and its other consumers (e.g. Secrets' Type picker, which has the same underlying characteristic) were left untouched, per scope discipline.
- The new `recent_projects` Workbench panel was registered on the frontend (`registerWorkbenchPanel`) but never added to the backend's `DEFAULT_LAYOUT_PANELS` (`app/services/workbench.py`), so it never appeared for fresh installs — a panel's registration alone doesn't make it appear; it must also be in the default panel list (existing panels like `recent_notes` already followed this two-sided pattern, Projects initially only did the frontend half). Fixed by adding `{"type": "recent_projects", "visible": True}` to `DEFAULT_LAYOUT_PANELS`, matching the `recent_notes` precedent; updated `test_workbench.py`'s hard-coded default-panel-count assertion (5 → 6) to match.

Security review: no findings. No credential/API-key material is ever stored on or returned by a Project; project-scoped AI runs delegate entirely to Model Playground's existing `runs.create_run()` (zero new outbound-call code); all new routes require a session; all inputs are Pydantic-validated with length bounds; no raw SQL string interpolation; deletion is confirmed and non-destructive (unscopes, never cascades).

## Architectural Decisions

- [ADR-0014](../../decisions/0014-project-data-model-shape.md) — Project data model shape (top-level table + additive nullable FKs, unscope-not-cascade on delete, AI config as provider/model string references only).

## Modified Files

Backend (new): `models/project.py`, `schemas/projects.py`, `services/projects/service.py` (+`__init__.py`), `api/routes/projects.py`, `alembic/versions/0008_projects.py`, `tests/test_projects_{service,api,migration}.py`.

Backend (modified, additive): `models/__init__.py`, `models/{secrets,note,document,model_playground}.py` (added `project_id`), `schemas/{secrets,notes,documents}.py` (added `project_id`), `services/{secrets,notes,documents}/service.py` (added `project_id` filter), `api/routes/{secrets,notes,documents}.py` (added `project_id` query param), `api/router.py` (wired `projects` router), `services/workbench.py` (added `recent_projects` to default panels), `tests/test_workbench.py` (updated default-panel-count assertion).

Frontend (new): `features/projects/` (api.ts, project-picker.tsx, project-card.tsx, project-form-dialog.tsx, project-delete-dialog.tsx, project-ai-config.tsx, project-ai-quick-run.tsx, workbench-panel.tsx), `app/(app)/projects/page.tsx`, `app/(app)/projects/[id]/page.tsx`.

Frontend (modified, additive): `features/{secrets,documents}/api.ts` and `features/notes/api.ts` (added `project_id`), `features/secrets/secret-form-dialog.tsx` (project picker field), `features/documents/document-sidebar.tsx` (project filter), `features/notes/note-card.tsx` (project-assignment popover), `app/(app)/{secrets,notes,documents}/page.tsx` (project filter + deep-link param), `lib/nav-registry.ts` (nav entry), `features/workbench/register-all.ts` (panel registration import).

Docs (new): `forge-docs/decisions/0014-project-data-model-shape.md`.

Docs (modified): all `forge-docs/implementation/Phase-06-Projects/*.md`, `forge-docs/03_ARCHITECTURE.md`, `forge-docs/02_ROADMAP.md`, `forge-docs/decisions/README.md`, `docs/API.md`, `docs/Database.md`, `docs/Security.md`, `.gitignore`.

## Next Milestone

None — phase complete.

## Next Claude Prompt

```
Phase 06 Projects is complete. No further work is queued for this phase.
```

## Session Notes

- 2026-07-20 — Phase scaffold created by the Lead Architect FDK setup. No implementation work has occurred.
- 2026-08-02 — Baseline inspection found every Phase 06 doc was an unfilled template; per `09_CLAUDE_CODE_RULES.md` §1–§2 this blocked implementation. Flagged to the user; user confirmed scope (grouping + per-project default AI provider/model referencing Phase 05) and approved the documentation-first path. Spec, acceptance criteria, and all supporting docs written; ADR-0014 resolved the data-model question. User gave explicit go-ahead to implement.
- 2026-08-03 — Backend and frontend implemented, tested, and manually QA'd in a real browser. Two real bugs found during QA (Select label rendering, missing default Workbench panel entry) and fixed. Security review completed, no findings. Full regression suite green (backend + frontend). Documentation finalized. Phase marked complete.

## Cross-references

- [README.md](README.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
- [../../history/README.md](../../history/README.md)
