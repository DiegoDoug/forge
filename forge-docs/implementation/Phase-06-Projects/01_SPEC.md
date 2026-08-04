# Projects — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Confirmed — ready for `IMPLEMENT.md` authorization
> **Last Updated:** 2026-08-02

---

## 1. Summary

Introduce **Projects** as a cross-feature grouping concept: a Project is a named workspace that Secrets, Notes, and Documents can optionally belong to, so a user working on one thing can see just that thing's secrets/notes/documents instead of one flat list each. A Project may also declare a **default AI provider/model** (referencing the existing Phase 05 provider abstraction) that AI actions run in that project's context use by default — no new credential system, no provider SDK coupling.

## 2. User stories

- As a user with several unrelated things going on (e.g. "Client A", "Home Lab", "Side Project"), I want to group my secrets, notes, and documents by project, so I can focus on one workspace's items without wading through everyone else's.
- As a user creating a new secret/note/document, I want to optionally assign it to a project at creation time (or later), so it shows up when I filter by that project.
- As a user viewing a project, I want to see counts and quick lists of the secrets, notes, and documents scoped to it, so the project page is a real workspace, not just a label.
- As a user who regularly asks AI things in the context of one project, I want to set that project's default AI provider and model once, so I don't re-pick it every time.
- As a user in a project with a default AI provider/model configured, I want to run a quick prompt without leaving the project and see the result, so the project is a usable workspace rather than just metadata.
- As a user who deletes a project, I want my secrets/notes/documents to remain intact (just unassigned), so deleting an organizational label never destroys my data.
- As a user on the Workbench, I want a "Recent Projects" panel (per ADR-0005), so Projects are reachable from my daily-use dashboard, not just a sidebar link.

## 3. Functional requirements

**Project CRUD**
- FR1. A user can create a Project with a name (required, 1–200 chars), an optional description (0–2000 chars), and a color (defaults to a swatch, same convention as Notes/Tags).
- FR2. A user can list all Projects, with each entry showing name, color, archived state, and counts of scoped secrets/notes/documents.
- FR3. A user can view a single Project's detail: its metadata, its AI configuration, and the lists of secrets/notes/documents scoped to it.
- FR4. A user can edit a Project's name, description, color, and archived flag.
- FR5. A user can archive a Project (soft — hides it from the default list, does not delete it or unscope its children) and unarchive it.
- FR6. A user can permanently delete a Project. Deleting a Project **never** deletes its secrets/notes/documents — every scoped entity's `project_id` is cleared (unscoped) as part of the delete. This is destructive to the Project row only and requires an explicit confirmation step (per `04_UI_GUIDELINES.md` §2).

**Scoping existing features**
- FR7. Secrets, Notes, and Documents each gain an optional `project_id`. It can be set at creation time or changed later (edit form / move action).
- FR8. The existing Secrets, Notes, and Documents list views can filter by project (a project picker alongside their existing filters — folder/tag for Secrets, archived for Notes, etc.).
- FR9. A Secret/Note/Document with no `project_id` is "unassigned" and continues to behave exactly as it does today (Projects is additive — nothing about existing behavior changes for unassigned items).

**AI configuration**
- FR10. A Project can declare a default AI provider and model, chosen from the set of providers currently in `PROVIDER_REGISTRY` (Phase 05 abstraction) — same list Model Playground shows, including which are "configured" (have a credential) vs. not.
- FR11. Setting a default provider/model does not require that provider to be configured yet (a user can plan ahead), but running an AI action against an unconfigured provider fails with a clear, actionable error (matches Model Playground's existing `provider_not_configured` error).
- FR12. A Project's detail page offers a quick "Run a prompt" action using its default provider/model. This delegates entirely to the existing Model Playground run pipeline (credential lookup, adapter dispatch, timeout, error handling) — it is not a second AI execution path.
- FR13. AI runs made through a Project are tagged with that project and appear in a "this project's recent AI activity" list on the Project detail page. They also remain visible in Model Playground's own run history (same underlying `PlaygroundRun` rows), unified rather than duplicated.
- FR14. No API key, provider credential, or secret material is ever stored on a Project. Only a provider key string and a model string (a reference, mirroring how `PlaygroundResult` already stores `provider`/`model` as plain strings).

**Workbench integration**
- FR15. A "Recent Projects" Workbench panel exists (per ADR-0005), following the exact registration pattern Notes already uses (`registerWorkbenchPanel`), showing the most recently updated non-archived projects with a link to create one when the list is empty.

**Navigation**
- FR16. Projects is reachable from the sidebar and the command palette, per `04_UI_GUIDELINES.md` §2.

## 4. Relationship to existing features

New organizational layer, per ADR-0014:

- **Secrets, Notes, Documents** each gain an additive, nullable, indexed `project_id` foreign key. No existing field, endpoint, or behavior changes for entities that don't set it.
- **Model Playground**: `PlaygroundRun` gains the same additive nullable `project_id`. Project-level AI actions call the existing `app.services.model_playground.runs.create_run()` — Projects introduces zero new outbound-call code and zero new credential storage. See ADR-0014 §2 for the full dependency chain (`Project → AI configuration → existing AI Provider Service → Provider Registry → Provider Adapter → Configured Provider`).
- **Workbench**: gains one new panel type (`recent_projects`), registered the same way Notes' `recent_notes` panel is — no Workbench core changes.

## 5. Explicitly out of scope

- Multi-project membership (an entity belonging to more than one project) — ADR-0014 §3 defers this; would need a join table and a follow-up ADR.
- Nested/sub-projects or project hierarchies.
- Per-project access control, sharing, or multi-tenant ownership — Forge remains single-tenant (per `03_ARCHITECTURE.md` §1.3); "project ownership" in the single-tenant sense means "which operator's browser" — not applicable, there is exactly one operator.
- A new provider/credential system, or any provider not already in `PROVIDER_REGISTRY` — reuse Phase 05 only.
- Deep AI features embedded inside Notes/Documents editors (e.g. inline AI-assisted editing) — that's a plausible future phase (Knowledge Hub or beyond), not Phase 06. Phase 06's AI surface is limited to: pick a default provider/model, run a standalone quick prompt from the Project page.
- Prompt Studio integration (prompts scoping into Projects) — ADR-0005 names it as a future candidate; not in this phase's functional requirements.
- Pagination of project lists — Forge-wide pagination is a tracked gap (`02_ROADMAP.md` §5); Phase 06 follows the existing convention (unpaginated lists, same as Notes/Documents today) rather than solving it here.

## 6. Open questions

None blocking — ADR-0014 resolved the data-model question; scope was confirmed directly by the user (grouping + per-project default AI provider/model, referencing Phase 05's abstraction, no duplicate credentials).

## 7. TODO

None — this document is confirmed, not a template placeholder.

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [04_DATABASE.md](04_DATABASE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../decisions/0005-projects-primary-organizational-unit.md](../../decisions/0005-projects-primary-organizational-unit.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
