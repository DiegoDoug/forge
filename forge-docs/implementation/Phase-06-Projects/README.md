# Projects — README

> **Purpose:** Entry point for the Projects phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** 🔒 RELEASED & FROZEN — tagged `v0.6.0-projects`, committed directly to `master` (commit `ddc8972`)
> **Last Updated:** 2026-08-03

---


## Objective

Introduce a cross-feature 'Project' grouping concept so Vault secrets, Notes, and Documents can be organized per project or workspace instead of one flat list each, with an optional per-project default AI provider/model built on the existing Phase 05 provider abstraction.

## Scope

**In scope:**
- [x] Project CRUD (create/list/get/update/archive/delete).
- [x] Optional `project_id` scoping on Secrets, Notes, Documents (additive — unassigned items behave exactly as today).
- [x] Project-level default AI provider/model selection, referencing the existing `PROVIDER_REGISTRY` (Phase 05) — no new credential storage.
- [x] A project-scoped AI "quick run" that delegates to the existing Model Playground run pipeline.
- [x] "Recent Projects" Workbench panel (per ADR-0005).
- [x] Sidebar + command palette navigation entry.

**Out of scope:**
- [ ] Multi-project membership per entity (see [ADR-0014](../../decisions/0014-project-data-model-shape.md) §3) — future phase if needed.
- [ ] Nested/sub-projects, per-project access control/sharing.
- [ ] Deep AI-assisted editing inside Notes/Documents — candidate for Knowledge Hub (Phase 07) or later.
- [ ] Prompt Studio scoping into Projects — named as a future candidate in ADR-0005, not this phase.
- [ ] List pagination — tracked as a pre-existing gap in `../../02_ROADMAP.md` §5, not solved here.

Full detail: [`01_SPEC.md`](01_SPEC.md).

## Relationship to the shipped application

New organizational layer. Touches the existing **Secrets**, **Notes**, and **Documents** data models via an additive, nullable `project_id` foreign key on each (resolved in [ADR-0014](../../decisions/0014-project-data-model-shape.md) — not a rewrite of any of them, not a join table for this phase).

- Related frontend: `frontend/features/secrets/`, `frontend/features/notes/`, `frontend/features/documents/`, `frontend/features/model-playground/` (read-only reuse)
- Related backend: `backend/app/services/secrets/`, `backend/app/services/notes/`, `backend/app/services/documents/`, `backend/app/services/model_playground/` (reused for AI execution, not modified)

## Deliverables

- [x] `projects` table + migration `0008_projects.py`, plus additive `project_id` columns on `secrets`/`notes`/`documents`/`playground_runs`.
- [x] `services/projects/`, `schemas/projects.py`, `api/routes/projects.py` (full CRUD + AI run endpoints).
- [x] `frontend/features/projects/` + `/projects` and `/projects/[id]` pages + nav entry.
- [x] Project-picker integration in Secrets/Notes/Documents forms and filters.
- [x] "Recent Projects" Workbench panel.
- [x] Backend test coverage per [`07_TESTING.md`](07_TESTING.md); lint/typecheck/build passing; manual QA pass recorded.

## Dependencies

Lands after Phase 05 (Model Playground, released as `v0.5.1-ai-providers`), which it depends on for the provider/model abstraction — satisfied. Should land before or alongside Phase 07 (Knowledge Hub), which likely assumes a similar grouping concept.

- [x] Phase 05 dependency confirmed complete before this phase's implementation begins.

## Milestones

- [x] Milestone 1 — Spec confirmed, backend implemented (data model, migration, service, API) and unit/integration-tested.
- [x] Milestone 2 — Frontend implemented (pages, feature module, cross-feature picker integration, Workbench panel) and manually QA'd.
- [x] Milestone 3 — Full regression pass, security review, documentation finalized, phase marked complete.

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- Cross-feature scope: touching Secrets (security-sensitive), Notes, and Documents simultaneously — mitigated by keeping every change additive/optional (see ADR-0014) so unassigned items are provably unaffected.
- AI integration risk: any temptation to duplicate credential handling — mitigated by delegating 100% of outbound AI calls to the existing `model_playground.runs.create_run()`.
- Migration risk on an existing populated database — mitigated by the guarded fresh-install-vs-upgrade pattern already established since `0006`, plus an explicit upgrade/downgrade/upgrade test.

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off.
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) — see [`../../history/2026-08-03-phase-06-final-checkpoint.md`](../../history/2026-08-03-phase-06-final-checkpoint.md).
- [x] Committed directly to `master` (commit `ddc8972`, no feature branch/PR for this release — see [`../../history/Phase-06/POST_IMPLEMENTATION_REVIEW.md`](../../history/Phase-06/POST_IMPLEMENTATION_REVIEW.md) "What Didn't"); release tagged `v0.6.0-projects`; implementation directory frozen; end-of-phase artifacts archived to [`../../history/Phase-06/`](../../history/Phase-06/).

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../history/Phase-06/10_RELEASE_NOTES.md](../../history/Phase-06/10_RELEASE_NOTES.md)
- [../../history/Phase-06/POST_IMPLEMENTATION_REVIEW.md](../../history/Phase-06/POST_IMPLEMENTATION_REVIEW.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
