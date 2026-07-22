# Project Initialization Engine — README

> **Purpose:** Entry point for the Project Initialization Engine phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** Lead Software Engineer (session-assigned, per project owner's Phase 02 kickoff instruction).
> **Status:** Implementation complete (all three milestones done, Docker-verified, browser-verified) — per [`../../13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), next stage is Release Candidate (an independent audit pass), then Owner Sign-off (requires the actual project owner) before Released/merge. Not yet merged to `master`.
> **Last Updated:** 2026-07-22

---

## Objective

Build a template-driven scaffolding engine that generates two kinds of file bundles on demand, as a downloadable zip, with no filesystem access to the host and no outbound network calls:

1. **FDK phase scaffolds** — a new `Phase-XX-Name/` folder (the same 13-file structure this document belongs to) for extending Forge's own FDK.
2. **AI project instruction files** — `CLAUDE.md`, `AGENTS.md`, and a generic `instructions.md`, populated from user-supplied project metadata, for use in *any* target project (not just Forge).

## Scope

**In scope:**
- [x] A template catalog covering the two kinds above.
- [x] A generation form for each kind (project/phase metadata in, files out).
- [x] Server-side rendering of templates via placeholder substitution (stdlib `string.Template`, no new templating dependency).
- [x] Packaging generated files into a single zip, returned as a download — never written to a host filesystem path.
- [x] A lightweight generation history (what was generated, when, with what inputs) so a user can re-download or reuse a prior configuration, surfaced via the existing Activity Log.
- [x] A new `/project-init` page reachable from the sidebar and command palette (`frontend/lib/nav-registry.ts`).

**Out of scope (see [01_SPEC.md](01_SPEC.md) §5 for full detail and reasoning):**
- [ ] Writing generated files directly to any path on the host filesystem or inside the Forge container. Download-only, by design (security: this app has no business writing outside its own data volume, and target projects are normally on a different machine on the LAN).
- [ ] A general-purpose, user-authored template editor (bring-your-own-template). Phase 02 ships a fixed, built-in catalog of two template kinds; a template-authoring UI is a candidate for a future phase, not this one.
- [ ] LLM-assisted content generation of any kind. This is pure templating — no outbound network calls, fully LAN-safe per [01_PRODUCT_PRINCIPLES.md §1.2](../../01_PRODUCT_PRINCIPLES.md).
- [ ] Workbench panel/pin registration for this feature. Phase 01 (Workbench) is released and frozen (`v0.1.0-workbench`); Phase 02 only adds a nav-registry entry (sidebar + command palette), which is the pre-existing, non-Workbench-owned reachability mechanism. Registering a Workbench panel for Project Init is a candidate future enhancement, not required here.
- [ ] Direct integration with Phase 06 (Projects). This phase creates project *scaffolds*; it does not know about Forge's own future Projects entity.

## Relationship to the shipped application

New capability. Consumes and extends [`forge-docs/templates/project-initialization/`](../../templates/project-initialization/README.md), whose actual template content now lives in `backend/app/services/project_init/templates/` (code, not user data — see [03_BACKEND.md](03_BACKEND.md) §1).

- Related frontend: new `frontend/features/project-init/` + `frontend/app/(app)/project-init/page.tsx`.
- Related backend: new `backend/app/services/project_init/` subpackage, `backend/app/api/routes/project_init.py`, one new table (`ProjectInitGeneration`).

## Deliverables

- [x] `GET /api/project-init/catalog` — the two template kinds and their input fields.
- [x] `POST /api/project-init/generate` — validates input, renders files, persists a history record, logs activity.
- [x] `GET /api/project-init/history` — recent generations (most recent first).
- [x] `GET /api/project-init/{id}/download` — re-renders and streams the zip for a past generation.
- [x] `DELETE /api/project-init/{id}` — removes a history record.
- [x] `/project-init` page: template picker → kind-specific form → generate → download, plus a history list with re-download/delete.
- [x] Alembic migration adding `project_init_generations`.
- [x] Unit tests (renderer, service) and integration tests (API routes).

## Dependencies

Benefits from Phase 01 (Workbench) existing as the natural entry point for launching it, but not hard-blocked by it — satisfied, Phase 01 is complete and released.

- [x] Phase 01 dependency status confirmed complete (`02_ROADMAP.md` §3: "✓ Complete — released & frozen as `v0.1.0-workbench`").

## Milestones

- [x] **Milestone 1 — Backend engine**: model, migration, schemas, `services/project_init/` (catalog + renderer + zip), API routes, backend tests passing.
- [x] **Milestone 2 — Frontend UI**: `features/project-init/api.ts`, forms, history list, `/project-init` page, nav-registry entry.
- [x] **Milestone 3 — Integration & release**: full build/lint/typecheck/test pass, Docker Compose build verified, browser-verified golden path for both template kinds, `CURRENT_STATE.md` and acceptance criteria finalized, checkpoint logged.

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- **Technical:** Template drift — the FDK phase scaffold's built-in templates could fall out of sync with the *real* 12-file structure documented in `02_ROADMAP.md` §5 / `11_PROJECT_STRUCTURE.md` §5, if that structure changes later without updating this phase's templates. Mitigated by generating the file *names* and section skeletons directly from the same structure this phase itself follows.
- **Product/UX:** Two template kinds in one form-driven UI risks feeling like two unrelated features bolted together. Mitigated by a single, shared "pick a kind → fill a form → download" flow (see [02_UI.md](02_UI.md)).
- **Existing-feature risk:** None — this is a wholly new, isolated feature (`services/project_init/`, `features/project-init/`); it does not touch Secrets, Notes, Documents, Generators, Crypto, Converters, Utilities, Ingest, Workbench, Search, or Settings.

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are checked off, with two honestly-flagged partial items (explicit Tab-key testing; pixel-level screenshot confirmation of dark mode/mobile — this environment's screenshot tool was unavailable, structural verification substituted) rather than falsely marked fully verified.
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
