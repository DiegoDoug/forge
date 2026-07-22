# Project Initialization Engine — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted — authorization pass complete (self-authorized per project owner's explicit instruction to treat spec+implementation as one continuous session; see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md)).
> **Version:** 1.0.0
> **Last Updated:** 2026-07-22
> **Depends On:** [../../00_VISION.md](../../00_VISION.md), [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md), [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
> **Supersedes:** v0.1 template placeholder of this document.

---

## 1. Summary

Build a scaffolding engine — the **Project Initialization Engine** — that generates structured file bundles from a small, fixed, built-in template catalog, and returns them to the user as a single zip download. Two template kinds ship in this phase:

1. **FDK Phase Scaffold** — generates a new `Phase-XX-Name/` folder matching the 13-file structure this very phase folder uses (`README.md`, `CURRENT_STATE.md`, `01_SPEC.md` … `09_IMPLEMENTATION_TASKS.md`, `10_RELEASE_NOTES.md`, `IMPLEMENT.md`), pre-filled with the phase number, name, and objective the user supplies. (Note: [`11_PROJECT_STRUCTURE.md §5`](../../11_PROJECT_STRUCTURE.md) describes this as a "12-file structure" — that count predates `10_RELEASE_NOTES.md` existing as a standard file; Phase 01 shipped without one. This phase's own folder and its generated output both include it, since the project owner's Phase 02 kickoff explicitly asked for a `10_RELEASE_NOTES.md`. Flagged as a minor, pre-existing doc/reality drift in [`CURRENT_STATE.md`](CURRENT_STATE.md) Known Issues rather than silently rewritten.)
2. **AI Project Instructions** — generates AI coding-assistant instruction files (`CLAUDE.md`, `AGENTS.md`, `instructions.md`) for an arbitrary target project, pre-filled with the project name, description, tech stack, and conventions the user supplies.

Both kinds are pure server-side templating (stdlib `string.Template` substitution) — no LLM calls, no outbound network access, and no writes to any filesystem path outside the app's own database. The user always ends up with a zip file they download and unpack wherever they want.

## 2. User stories

- As a developer maintaining Forge's own FDK, I want to generate a new `Phase-XX-Name/` folder with the correct 12-file skeleton already in place, so I don't have to hand-copy and rename an existing phase's files every time a new phase is proposed.
- As a developer starting a new side project, I want to generate a `CLAUDE.md`/`AGENTS.md`/`instructions.md` set pre-filled with my project's name, description, and tech stack, so my AI coding assistant has real project context from commit one instead of a blank file.
- As a developer, I want to pick only the instruction files I actually need (e.g. just `CLAUDE.md`, not all three), so I don't get files for tools I don't use.
- As a developer, I want my last few generations remembered, so I can re-download a bundle I generated earlier without re-entering everything, or quickly delete one I don't need anymore.
- As a developer, I want the generated files to show up in Forge's existing Recent Activity, so this feature doesn't feel like a bolted-on side tool with its own separate history UI.
- As a developer, I want this reachable from the sidebar and the command palette like every other Forge feature, so I don't have to remember a URL.

## 3. Functional requirements

1. A new page at `/project-init` presents exactly two generation kinds: **FDK Phase Scaffold** and **AI Project Instructions**. The user picks one before a form appears (see [02_UI.md](02_UI.md) §1).
2. **FDK Phase Scaffold** form fields: phase number (integer, e.g. `9`), phase name (string, e.g. `Knowledge Hub`), one-line objective/summary (string). Output: the 13 files this phase folder itself uses (see §4 note above), each pre-filled with the phase number/name in headers and cross-references, the objective in `README.md` §Objective and `01_SPEC.md` §1, and every other section left as the same `[ ] TODO` scaffold structure the real FDK templates use (i.e. the generated output is a real, usable starting point — not a lorem-ipsum stub).
3. **AI Project Instructions** form fields: project name (string), one-paragraph description (string), tech stack (list of free-text tags, e.g. `Next.js`, `FastAPI`, `Postgres`), key conventions/rules (free-text, optional, multi-line), and a checklist of which output files to include: `CLAUDE.md`, `AGENTS.md`, `instructions.md` (at least one must be selected). Output: only the selected files, each populated with the supplied project name, description, tech stack, and conventions in the format that file's convention expects (see [03_BACKEND.md](03_BACKEND.md) §2 for the per-file template shape).
4. Generating either kind returns a single `.zip` file the browser downloads immediately — never a page of raw text to copy, and never a write to any path on the server's filesystem or the user's filesystem chosen implicitly (the browser's own download mechanism decides where it lands, per normal browser behavior).
5. Every successful generation is recorded: kind, a short name (phase name, or project name), the input configuration, and a timestamp. This record is what powers requirement 6 and 7 below — the zip itself is not stored as a blob; it is deterministically re-rendered from the stored configuration on each download (same pattern as Documents' export-on-demand, see [`backend/app/services/documents/export.py`](../../../backend/app/services/documents/export.py)).
6. A history list on `/project-init` shows the last 20 generations (most recent first), each re-downloadable and deletable.
7. Every successful generation writes one `ActivityLog` row (`action=created`, `entity_type=project_init_generation`), so it appears in the existing Recent Activity panel/page without any change to Recent Activity's own code.
8. The page is reachable from the sidebar and the command palette via a new `frontend/lib/nav-registry.ts` entry, per [`04_UI_GUIDELINES.md §2`](../../04_UI_GUIDELINES.md).
9. Input validation: phase number must be a positive integer; all text fields have a sane max length (enforced both client-side, via plain field checks matching every other Forge tool form, and server-side via Pydantic) to prevent absurdly large generated files; at least one output file must be selected for AI Project Instructions.
10. Deleting a history record removes only the history row — it has no effect on any file the user already downloaded (Forge never tracks what happens to a zip after the browser receives it).

## 4. Relationship to existing features

New capability — isolated in `backend/app/services/project_init/`, `backend/app/api/routes/project_init.py`, and `frontend/features/project-init/`, per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) feature isolation. Reuses, without modifying:

- The existing `ActivityLog` model/service (`backend/app/services/activity.py`) for requirement 7.
- The existing nav-registry pattern (`frontend/lib/nav-registry.ts`) for requirement 8.
- The existing thin-router/service-layer split, Pydantic schema convention, and TanStack Query `api.ts` convention used by every other feature.

Consumes and extends [`forge-docs/templates/project-initialization/`](../../templates/project-initialization/README.md) — the actual template *content* now lives as code under `backend/app/services/project_init/templates/`, per that document's own note that "no engine logic" belongs in `forge-docs/templates/`.

No existing table, model, service, or frontend feature is modified by this phase.

## 5. Explicitly out of scope

- **Writing generated files to any filesystem path.** Forge is a self-hosted app a user may run on different hardware than their actual project lives on; there is no safe, general way to "write to the user's project folder" from a server process. Download-only is not a shortcut — it is the correct design for a LAN-deployed tool with no assumed access to the user's other filesystems. A future phase could add a CLI companion that unzips locally, but that is out of scope here.
- **A user-facing template editor / bring-your-own-template system.** The catalog is fixed and built-in for this phase. Making templates end-user-editable is a real feature with its own UI, validation, and security surface (arbitrary template injection into generated files) — deferred, not silently half-built.
- **Any LLM-assisted content generation.** "AI project instruction files" describes the *output's purpose* (files that instruct an AI coding assistant), not files generated *by* an AI. No provider/API-key concept, no outbound network calls — this stays fully LAN-safe per [`01_PRODUCT_PRINCIPLES.md §1.2`](../../01_PRODUCT_PRINCIPLES.md), and does not trigger the "new outbound network call" review flagged in [`03_ARCHITECTURE.md §4`](../../03_ARCHITECTURE.md) for Prompt Studio/Model Playground.
- **Workbench panel or pinned-tool registration.** Phase 01 is released and frozen (`v0.1.0-workbench`, [ADR-0009](../../decisions/0009-phase-specification-freeze.md) pattern). This phase adds only a nav-registry entry (sidebar + command palette reachability), which is not Workbench-owned code. A future Workbench-side enhancement (a "New scaffold" quick action) is a candidate to propose *to* a future Workbench-touching phase, not something this phase does itself.
- **Any relationship to Forge's own future Phase 06 "Projects" entity.** This phase's output is a downloadable project scaffold; it has no data-model relationship to Forge's internal project-grouping concept.
- **Generating anything beyond the two named kinds** (e.g. a generic "any file template" system, License file generators, `.gitignore` generators). Two kinds, fully built, beats five kinds half-built, per [`01_PRODUCT_PRINCIPLES.md §1.3`](../../01_PRODUCT_PRINCIPLES.md).
- **Multi-file editing/preview before download.** The user picks a kind, fills the form, and downloads; there is no in-app rich preview/edit step before the zip is produced (a lightweight read-only file-list-with-expandable-content preview, not an editor, is included per [02_UI.md](02_UI.md) §1 — editing before download is what's out of scope).

## 6. Open questions

None blocking. All scope decisions above were resolved during this session by the Lead Software Engineer against the standing principles in [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) and [`03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) rather than deferred — see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md) for the authorization record, since no project owner was available synchronously to ratify this spec the way Phase 01's three review passes were ratified.

## 7. TODO

- [ ] TODO: Get retroactive project-owner sign-off on the scope decisions in §5 next time the project owner is available (self-authorized per explicit session instruction — see [`CURRENT_STATE.md`](CURRENT_STATE.md) Session Notes).

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [04_DATABASE.md](04_DATABASE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
