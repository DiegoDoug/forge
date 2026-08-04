# Projects — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Complete — all tasks done
> **Last Updated:** 2026-08-03

---

## 1. Task list

- [x] T1 — Backend model: `models/project.py` (`Project`), register in `models/__init__.py`; add `project_id` columns to `models/secrets.py::Secret`, `models/note.py::Note`, `models/document.py::Document`, `models/model_playground.py::PlaygroundRun`.
- [x] T2 — Migration `alembic/versions/0008_projects.py` (create `projects`, add four `project_id` columns/indexes), guarded for both fresh-install and upgrade paths per `04_DATABASE.md` §3.
- [x] T3 — Schemas: `schemas/projects.py` (Create/Update/Out/SummaryOut/AiRunIn), reusing `model_playground` provider/model validators; add `project_id` to Secret/Note/Document schemas.
- [x] T4 — Service: `services/projects/service.py` (CRUD, counts, delete-unscopes, `run_project_prompt`, `list_project_runs`); add `project_id` filter to `notes/service.py`, `documents/service.py`, `secrets/service.py`.
- [x] T5 — Routes: `api/routes/projects.py`, wired into `api/router.py`; add `project_id` query param to existing list routes.
- [x] T6 — Backend tests: `test_projects_service.py`, `test_projects_api.py`, migration up/down/up test, and extensions to existing Secrets/Notes/Documents/Model Playground test files.
- [x] T7 — Frontend feature module: `features/projects/api.ts` + all components listed in `05_COMPONENTS.md` §1.
- [x] T8 — Frontend pages: `app/(app)/projects/page.tsx`, `app/(app)/projects/[id]/page.tsx`; nav entry in `lib/nav-registry.ts`.
- [x] T9 — Frontend integration: project picker wired into Secrets/Notes/Documents forms and list filters; Workbench panel registered via `register-all.ts`.
- [x] T10 — Regression pass: full backend test suite, frontend lint/typecheck/build, fix any failures caused by this phase.
- [x] T11 — Manual browser QA per `07_TESTING.md` §3; fix any bugs found and re-verify.
- [x] T12 — Security review (per mission §10) + documentation pass: update `docs/API.md`, `docs/Architecture.md`/`docs/Database.md` if they enumerate tables/endpoints, `02_ROADMAP.md` status row, this phase's `CURRENT_STATE.md` and `README.md` to their final "complete" state.

> Reminder: 10–12 completed tasks is itself a checkpoint trigger — see `../../10_CHECKPOINT_PROTOCOL.md` §1.

## 2. Task ordering notes

Hard sequencing: T1 → T2 (model before migration) → T3 → T4 → T5 (schema → service → route) → T6 can start once T5 lands but individual unit tests for T4 may be written alongside T4. T7 (frontend api.ts) depends on T5's real response shapes being stable. T8/T9 depend on T7. T10 depends on everything through T9. T11 depends on T10 passing. T12 is last, folding in anything discovered during T10/T11.

## 3. TODO

None — this document is confirmed, not a template placeholder.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
