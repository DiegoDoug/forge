# Prompt Studio — README

> **Purpose:** Entry point for the Prompt Studio phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** 🔒 RELEASED & FROZEN — tagged `v0.3.0-prompt-studio`, merged to `master` via [PR #18](https://github.com/DiegoDoug/forge/pull/18). Specification: Locked. Implementation: Closed. Future changes: bug fixes only.
> **Last Updated:** 2026-07-23

---

## Executive Summary

Prompt Studio gives a developer a dedicated workspace to author, structure, and version-control LLM prompts inside Forge — the same way Secrets already gives them versioned, encrypted credential storage. A prompt is a body of text with named, typed variables; the workspace renders a live, client-side preview of the substituted text, tracks every content edit as an immutable version, and lets a prompt be duplicated to seed a new one. **This phase does not call out to any LLM provider** — see "Relationship to the shipped application" below for why, and [`01_SPEC.md`](01_SPEC.md) §4–§5 for the full reasoning.

## Problem Statement

Today, a Forge user who wants to reuse a well-crafted prompt has nowhere to keep it except a Note, a Document, or an external tool — none of which are built for "the same shape, different values every time," and none track how the wording changed over time. Every other kind of durable, structured, versioned content in Forge (Secrets, Notes, Documents) already has a dedicated home; prompts don't.

## Goals

- Give prompts a first-class, structured home: name, description, tags, body, and typed variables — not a Note with conventions layered on top.
- Never lose a previous wording: every content change is an immutable, restorable version.
- Make "reuse this prompt's shape" a first-class action (Duplicate), not a copy-paste workaround.
- Let a user see the fully-substituted result before they use a prompt anywhere else, without leaving Forge or calling any external service.
- Reach the feature the same way every other Forge tool is reached: sidebar, command palette, Recent Activity.

## Non-Goals

- Executing a prompt against a real LLM provider (OpenAI, Anthropic, etc.) — explicitly deferred; see "Relationship to the shipped application" below.
- A distinct "Template" entity or gallery separate from "Prompt" — every prompt already doubles as a template via Duplicate.
- Folders, nested organization, import/export, or multi-user sharing — see [`01_SPEC.md`](01_SPEC.md) §5 for the full list and reasoning.

## Scope

**In scope:**
- [x] Create/read/update/delete a prompt: name, description, tags, body, typed variable declarations.
- [x] Client-side, no-network render preview of a prompt's body with variable values substituted.
- [x] Immutable version history on every content (body/variables) change, with diff-between-versions and restore.
- [x] Duplicate ("use as template") to seed a new prompt from an existing one.
- [x] Search-by-name/description and filter-by-tag over the prompt list.
- [x] Activity Log integration (create/update/restore/duplicate/delete all appear in existing Recent Activity).
- [x] A new `/prompt-studio` page reachable from the sidebar and command palette.

**Out of scope (see [`01_SPEC.md`](01_SPEC.md) §5 for full detail and reasoning):**
- [ ] Live execution of a prompt against any real LLM provider — no outbound network calls, no API keys, in this phase.
- [ ] A separate Template entity/gallery distinct from Prompt.
- [ ] Folders/nested organization beyond tags.
- [ ] Server-side pagination (matches the existing, already-tracked gap shared by every other list endpoint today).
- [ ] Import/export or sharing/collaboration features.
- [ ] Non-scalar variable types (arrays, objects, files).

## Relationship to the shipped application

New capability, isolated in `backend/app/services/prompt_studio/`, `backend/app/api/routes/prompt_studio.py`, and `frontend/features/prompt-studio/`.

`02_ROADMAP.md` §4 and `03_ARCHITECTURE.md` §3–4 both flag "Prompt Studio and Model Playground share LLM-provider plumbing — TODO: confirm build order" as an open question. **This is resolved for Phase 03**: rather than build shared provider plumbing ahead of Phase 05's own specification, Prompt Studio ships with zero outbound network calls and zero provider/API-key concepts this phase. This was confirmed directly with the project owner during specification (not assumed) — see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md). Whatever "run this prompt against a provider" experience Phase 05 eventually builds will consume a Prompt Studio prompt as an input when Phase 05 itself is specified; it is not built here.

- Related frontend: new `frontend/features/prompt-studio/` + `frontend/app/(app)/prompt-studio/page.tsx`.
- Related backend: new `backend/app/services/prompt_studio/` subpackage, `backend/app/api/routes/prompt_studio.py`, two new tables (`Prompt`, `PromptVersion`).
- Reuses, unmodified: `ActivityLog` service, `nav-registry.ts` pattern, `string.Template` substitution (already used by `services/project_init/renderer.py`), the `diff` npm package (already used by the Converters diff viewer), `@monaco-editor/react` (already a frontend dependency).

## Deliverables

- [ ] `GET /api/prompts` — list prompts (search/tag filter, lightweight list shape).
- [ ] `POST /api/prompts` — create a prompt (validates body against declared variables, logs activity, seeds version 1).
- [ ] `GET /api/prompts/{id}` — full detail (current body, variables, tags).
- [ ] `PATCH /api/prompts/{id}` — metadata-only update (name/description/tags — no version bump).
- [ ] `PUT /api/prompts/{id}/content` — body/variables update (creates a new version, logs activity).
- [ ] `DELETE /api/prompts/{id}` — delete, cascades to versions, logs activity.
- [ ] `POST /api/prompts/{id}/duplicate` — clone into a new prompt, logs activity.
- [ ] `GET /api/prompts/{id}/versions` — version history (lightweight list shape, newest first).
- [ ] `GET /api/prompts/{id}/versions/{version_id}` — one version's full content.
- [ ] `POST /api/prompts/{id}/versions/{version_id}/restore` — restore, snapshotting current content first, logs activity.
- [ ] `/prompt-studio` page: master-detail list + editor, variable editor, client-side render preview, version history with diff and restore.
- [ ] Alembic migration `0005_prompt_studio.py` adding `prompts` and `prompt_versions`.
- [ ] Unit tests (service layer: create/update/version-bump/restore/duplicate/cascade-delete) and integration tests (API routes).

## Dependencies

No hard dependency on any other phase. Benefits from Phase 01 (Workbench) as the entry point and Phase 02's Activity Log/nav-registry conventions, both already complete and released.

- [x] Phase 01 dependency status confirmed complete (`02_ROADMAP.md` §3: "✓ Complete — released & frozen as `v0.1.0-workbench`").
- [x] Phase 02 dependency status confirmed complete (`02_ROADMAP.md` §3: "✓ Complete — released & frozen as `v0.2.0-project-init`").
- [x] The Phase 03/Phase 05 "shared LLM-provider plumbing" sequencing question is resolved — Phase 03 has no dependency on Phase 05, and introduces no plumbing for Phase 05 to inherit (see "Relationship to the shipped application" above).

## Milestones

> Finalized in Stage 2 (Technical Planning, authorized 2026-07-22 alongside this specification) as four milestones of 3–5 tasks each, per the project owner's explicit constraint — see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) for the full task-by-task breakdown (objective, files, implementation/testing tasks, completion criteria per milestone).

- [x] Milestone 1 — **Backend data layer** (T1–T4): `Prompt`/`PromptVersion` models, `0005_prompt_studio.py` migration, Pydantic schemas + validators, deterministic `templating.py`. Verifiable with `pytest` alone — no server needs to run. **Complete 2026-07-22** — see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) Milestone 1 for verification detail.
- [x] Milestone 2 — **Service layer & API** (T5–T9): full CRUD/versioning/duplicate/restore business logic in `services/prompt_studio/service.py`, thin API routes, full backend test suite green. **Complete 2026-07-22** — see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) Milestone 2 for verification detail, including a shared-code bug fix in `app/core/errors.py`.
- [x] Milestone 3 — **Frontend foundation** (T10–T13): `features/prompt-studio/api.ts`, list/editor/variables/body-editor/preview components, `/prompt-studio` page, nav-registry entry. Create → edit → preview → save → copy works end-to-end in a real browser. **Complete 2026-07-22**, implemented together with Milestone 4's version-history/restore/duplicate/delete UI per the project owner's explicit 11-step authorization — see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) Milestones 3–4.
- [x] Milestone 4 — **Versioning UI, integration & release readiness** (T14–T17): version history/diff/restore/duplicate/delete UI, full UI polish pass (found and fixed a real Monaco rendering bug and a missing responsive-collapse gap), Docker Compose full-stack verification (isolated clean-room stack, full golden path, restart + persistence confirmed), and formal acceptance criteria close-out (found and fixed a missing client-side-validation gap and a silent Copy-error gap) — all **complete 2026-07-22**. See [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) and [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) for full detail. Phase 03 is implementation-complete and ready for Stage 4 (RC Audit).

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- **Technical:** Save-time placeholder validation (rejecting a body that references an undeclared `${name}`) could feel overly strict if a user genuinely wants literal `$` text in a prompt body (e.g. a prompt about shell scripting that legitimately contains `${VAR}`-shaped shell syntax). Mitigated by scoping the validation to exactly the declared-variable-name check (not a blanket "no `$` allowed") and documenting an escape hatch (`$$` renders a literal `$` per `string.Template`'s own escaping rule) in the UI's inline help — see [`02_UI.md`](02_UI.md) §5.
- **Product/UX:** Versioning-on-every-content-save could produce a very long history for a prompt edited frequently in small increments (e.g. one word at a time). Accepted as a reasonable cost of "never lose a wording" — Secrets already accepts the same tradeoff, and there is no measured evidence yet that it's a real problem worth debouncing or squashing against.
- **Existing-feature risk:** None — this is a wholly new, isolated feature (`services/prompt_studio/`, `features/prompt-studio/`); it does not touch Secrets, Notes, Documents, Generators, Crypto, Converters, Utilities, Ingest, Workbench, Search, Project Init, or Settings.
- **Scope-boundary risk:** The strongest risk to this phase is scope creep toward "just add one provider call, it's easy" once the Monaco editor and preview are working and a live test feels one step away. The explicit Non-Goal in this document and `01_SPEC.md` §5 exists specifically to hold that boundary — implementation sessions must treat it as settled, not revisit it without a new project-owner conversation.

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off, with five items honestly filed as QA tickets (real Monaco keyboard input, dialog Escape/focus-trap under a trusted gesture, pixel-level dark-mode/responsive screenshots, the Copy success toast, high-DPI scaling) rather than falsely marked verified — this environment structurally cannot exercise them.
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) — Stage 3 (Implementation) is complete; next is Stage 4 (RC Audit).

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
