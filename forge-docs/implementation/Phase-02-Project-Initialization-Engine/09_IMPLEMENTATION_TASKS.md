# Project Initialization Engine — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Confirmed — ready for execution.
> **Last Updated:** 2026-07-22

---


## 1. Task list

- [x] T1 — Branch: create and switch to `Phase02/Project-Initialization-Engine` off `master`.
- [x] T2 — Backend model: `app/models/project_init.py` (`ProjectInitGeneration`), registered with `SQLModel.metadata`.
- [x] T3 — Backend migration: `alembic/versions/0004_project_init.py` (additive, `project_init_generations` table).
- [x] T4 — Backend schemas: `app/schemas/project_init.py` (`FieldSpec`, `TemplateKindOut`, `TemplateCatalogOut`, `FdkPhaseConfig`, `AiInstructionsConfig`, `GenerateRequest`, `GenerationOut`, `GenerationListOut`).
- [x] T5 — Backend catalog + templates: `services/project_init/catalog.py` + `services/project_init/templates/fdk_phase/*` (13 files) + `services/project_init/templates/ai_instructions/*` (3 files).
- [x] T6 — Backend renderer + zipper: `services/project_init/renderer.py`, `services/project_init/zipper.py`.
- [x] T7 — Backend service: `services/project_init/service.py` (generate/list_history/get_or_404/delete, activity logging).
- [x] T8 — Backend routes: `api/routes/project_init.py` + registration in `api/router.py`.
- [x] T9 — Backend tests: unit (renderer, zipper, service) + integration (API), per [`07_TESTING.md`](07_TESTING.md) §1. All 73 backend tests green (26 new + 47 pre-existing, zero regressions).
- [x] T10 — Frontend API layer: `features/project-init/api.ts` (hooks per [`05_COMPONENTS.md`](05_COMPONENTS.md) §4).
- [x] T11 — Frontend components: `kind-picker.tsx`, `fdk-phase-form.tsx`, `ai-instructions-form.tsx`, `file-preview.tsx`, `generation-actions.ts`, `generation-history.tsx`. Built with plain `useState` (not `react-hook-form`/`zod`) to match the pattern every existing Forge tool form actually uses — see [02_UI.md](02_UI.md)/[05_COMPONENTS.md](05_COMPONENTS.md) correction notes.
- [x] T12 — Frontend page + nav: `app/(app)/project-init/page.tsx`, `frontend/lib/nav-registry.ts` entry.
- [x] T13 — Validation: backend test suite green (73/73), frontend build/lint green (zero errors/warnings), `docker compose build` + full stack boot succeeded with migration `0003→0004` applied automatically, manual browser verification per [`07_TESTING.md`](07_TESTING.md) §3 completed for both template kinds (generate, download, history, delete, sidebar, command palette, empty/loading states, mobile viewport, dark mode).
- [x] T14 — Docs: `CURRENT_STATE.md`, this file, and the `history/` checkpoint log entry updated; `forge-docs/templates/project-initialization/README.md` already pointed at the real content location during T5.

> Reminder: 10–12 completed tasks is itself a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1. T1–T12 (12 tasks) is one checkpoint window; T13–T14 close out the phase.

## 2. Task ordering notes

Hard sequencing: T2 → T3 (model before migration) → T4 → T5 → T6 → T7 (schemas before catalog/templates before renderer/zipper before service) → T8 (service before routes) → T9 (implementation before its tests). T10 depends on T8 (frontend needs a real API contract to type against). T11 depends on T10. T12 depends on T11. T13 depends on everything. T1 has no dependency and runs first.

## 3. TODO

None — this document is confirmed and implementation-ready.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
