# Prompt Studio — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved by the project owner 2026-07-22 (Stage 1 COMPLETE, Stage 2 AUTHORIZED; see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md)). No changes without explicit approval, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) "Specification → Authorized."
> **Version:** 1.0.0
> **Last Updated:** 2026-07-22
> **Depends On:** [../../00_VISION.md](../../00_VISION.md), [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md), [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
> **Supersedes:** v0.1 template placeholder of this document.

---

## 1. Summary

Prompt Studio is an authoring and versioning workspace for reusable LLM prompts. A user writes a prompt's body text with named placeholder variables (e.g. `${audience}`), declares those variables with a type, a required/optional flag, and an optional default, and Prompt Studio renders a preview of the final text with sample values substituted in — entirely client-side, with no outbound network call. Every content edit is kept as an immutable version so a user can review history, diff two versions, or restore an older one without losing anything in between. A prompt can be duplicated to start a new one from an existing shape — this **is** Prompt Studio's "reusable template" mechanism: any saved prompt already doubles as a template for the next one.

**This phase does not execute prompts against a real LLM provider.** See §4 and §5 for why, and the Executive Summary in [`README.md`](README.md) for the scope decision this rests on.

## 2. User stories

- As a developer who repeats the same prompt shape across projects (a code-review rubric, a commit-message generator, a summarization instruction), I want to save it once with named variables, so I can reuse it without retyping or hunting through old chat history.
- As a developer iterating on a prompt's wording, I want every saved change kept as a numbered version, so I can compare "what changed between v3 and v4" and understand why an earlier version worked better.
- As a developer who broke a previously-working prompt with an edit, I want to restore an earlier version, so I don't have to reconstruct it from memory or version-control history I never kept.
- As a developer starting a new prompt that's a close variant of an existing one, I want to duplicate it, so I get the same variables and structure as a starting point instead of a blank editor.
- As a developer with many saved prompts, I want to search by name and filter by tag, so I can find the one I need without scrolling a long flat list.
- As a developer filling in a prompt's variables before copying it elsewhere (a chat UI, an API call, a teammate), I want a live preview of the fully-substituted text, so I can catch a missing or malformed variable before I paste it somewhere that matters.
- As a developer, I want this reachable from the sidebar and the command palette like every other Forge tool, so I don't have to remember a URL.
- As a developer, I want prompt creation, edits, restores, and deletes to show up in Forge's existing Recent Activity, so this doesn't feel like a bolted-on tool with its own separate history UI.

## 3. Functional requirements

1. A new page at `/prompt-studio` presents a master-detail layout: a searchable, tag-filterable list of saved prompts on one side, and the selected prompt's editor on the other (see [`02_UI.md`](02_UI.md) §1 for exact layout).
2. **Create a prompt**: name (required, ≤200 chars), optional description (≤1000 chars), optional tags (≤10 tags, ≤30 chars each), a body (required, ≤20,000 chars), and zero or more variable declarations. A newly created prompt starts at version 1.
3. **Variable declaration**: each variable has a `name` (must match `^[A-Za-z_][A-Za-z0-9_]{0,63}$`, unique within the prompt), a `type` of `string`, `number`, or `boolean`, a `required` flag, an optional `default` value (type-matched), and an optional `description` (≤500 chars). A prompt may declare at most 50 variables.
4. **Placeholder syntax and validation**: a variable is referenced in the body as `${name}` (Python `string.Template` syntax — the same substitution mechanism already used by [`services/project_init/renderer.py`](../../../backend/app/services/project_init/renderer.py), so no new templating dependency is introduced, per [`06_TECH_STACK.md`](../../06_TECH_STACK.md) §4). Saving a prompt's content is rejected (422) if the body references a `${name}` that is not a declared variable — this catches typos server-side rather than silently rendering a literal `${typo}` at preview time.
5. **Client-side render preview**: the editor has a "Preview" panel where the user can type or accept default ad hoc values for each declared variable and see the fully-substituted body update live, using the exact same `${name}` substitution algorithm as the backend's save-time validation (documented once in §4 above so both implementations stay in lockstep — see [`03_BACKEND.md`](03_BACKEND.md) §2 for the shared algorithm spec). This preview never leaves the browser and never calls any backend endpoint per keystroke, matching the existing client-side pattern used by Forge's Converters (JSON/regex/diff). A required variable left blank in the preview form shows the placeholder highlighted as unresolved rather than silently rendering empty string.
6. **Copy rendered output**: a "Copy" action copies the current preview's fully-substituted text to the clipboard, with the same visual confirmation pattern as every other copy-to-clipboard action in Forge (per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2).
7. **Versioning**: any change to a prompt's `body` or `variables` (not its `name`/`description`/`tags`, which are metadata-only edits) creates a new immutable version — the pre-change body and variables are snapshotted, the version counter increments, and the prompt's current content becomes the new value. This mirrors the existing Secrets versioning pattern (`backend/app/models/secrets.py`'s `SecretVersion`, snapshot-before-overwrite, cascade-delete with parent, newest-first ordering).
8. **Version history**: a "History" view lists every version of a prompt (version number, timestamp, and an auto-generated note such as "Edited", "Restored from v2"), newest first. Selecting two versions shows a diff of their bodies, rendered with the existing `diff` npm package already in the frontend dependency table (the same library backing the Converters diff viewer) — no new dependency.
9. **Restore a version**: restoring version N snapshots the prompt's current content as a new version first (so nothing is ever lost), then makes version N's body/variables the prompt's new current content, incrementing the version counter again. A restore requires an explicit confirmation step (per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2 — it changes what "current" means for the prompt, even though it's non-destructive to history).
10. **Duplicate ("Use as template")**: duplicating a prompt creates a brand-new prompt (its own id, its own version history starting at version 1) with the source's current body, variables, and tags copied in and the name suffixed `(copy)`. Version history is not carried over — the duplicate is a fresh, independent entity.
11. **Search and filter**: the list view supports a free-text search over name/description and a tag filter, applied client-side against the fetched list (no server-side pagination — matching the existing, explicitly-tracked gap noted in [`02_ROADMAP.md`](../../02_ROADMAP.md) §5 rather than introducing new pagination conventions in this phase).
12. **Delete**: deleting a prompt requires confirmation (per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2) and cascades to delete all of its versions. There is no "undo" — this matches the destructive-delete pattern already used by Secrets/Notes/Documents.
13. Every create, content-update, restore, duplicate, and delete writes one `ActivityLog` row via the existing `backend/app/services/activity.py` `record()` function, unmodified, so these actions appear in the existing Recent Activity panel/page (see [`03_BACKEND.md`](03_BACKEND.md) §3 for the exact action/summary mapping).
14. The page is reachable from the sidebar and the command palette via a new `frontend/lib/nav-registry.ts` entry, per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2.
15. All input validation is enforced both client-side (`zod` + `react-hook-form`, matching every other Forge form) and server-side (Pydantic schemas) — client-side validation is a UX convenience, never the only enforcement.
16. **Rendering determinism (added at project-owner request during specification review, 2026-07-22).** Both the backend's save-time validation substitution and the frontend's client-side preview substitution (requirement 5) perform **only**:
    - variable substitution (`${name}` → the supplied/default value)
    - escaping (`$$` → a literal `$`, per `string.Template`'s own rule)
    - validation (is every referenced name declared? is every required variable supplied?)

    Rendering **must never** execute scripting, expressions, conditionals, loops, function calls, filters, includes, or imports of any kind — there is no interpreted logic in a prompt body beyond straight name-for-value substitution. In one line:

    ```
    Prompt + Variables = Rendered Prompt
    ```

    Nothing more. This is a hard constraint on the implementation, not just a starting scope: it rules out ever reaching for a general-purpose templating engine (Jinja2 and similar all support conditionals/loops/filters/includes by design) as a "convenient" way to add a feature later — if a future request needs conditional logic in a prompt, that is a new, explicitly-scoped decision (a new ADR), not an incremental extension of `string.Template`-based rendering. This guarantee is what keeps Prompt Studio "an authoring tool, not an execution tool" (see [`README.md`](README.md) Executive Summary) — the same guarantee that makes the zero-outbound-calls decision in this section trustworthy: a prompt body can never itself become code that does something unexpected when rendered.

## 4. Relationship to existing features

New capability — isolated in `backend/app/services/prompt_studio/`, `backend/app/api/routes/prompt_studio.py`, and `frontend/features/prompt-studio/`, per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) feature isolation. Reuses, without modifying:

- The existing `ActivityLog` model/service (`backend/app/services/activity.py`) for requirement 13.
- The existing nav-registry pattern (`frontend/lib/nav-registry.ts`) for requirement 14.
- The existing thin-router/service-layer split, Pydantic schema convention, and TanStack Query `api.ts` convention used by every other feature.
- The existing `string.Template` placeholder-substitution approach already established by `services/project_init/renderer.py` (requirement 4) — no new templating library.
- The existing `diff` npm package already powering the Converters diff viewer (requirement 8) — no new diffing library.
- The existing `@monaco-editor/react` dependency for the prompt body editor (already in [`06_TECH_STACK.md`](../../06_TECH_STACK.md) §1) — no new editor dependency.
- The versioning *shape* pioneered by Secrets (`SecretVersion`: snapshot-before-overwrite, cascade-delete, newest-first) — copied as a pattern, not a shared table or shared code (Prompt Studio does not import from `services/secrets`, per feature isolation).

**Explicitly does not share code or a table with Phase 05 (Model Playground)**, despite `02_ROADMAP.md` §4 and `03_ARCHITECTURE.md` §3–4 flagging "shared LLM-provider plumbing" between the two as an open sequencing question. That question is resolved for this phase as follows: **Prompt Studio introduces zero outbound network calls, zero provider/API-key concepts, and zero new runtime dependencies in this phase** (see §5). Whatever "send this prompt to a provider" experience Phase 05 eventually builds will *consume* a saved Prompt Studio prompt (by id, or by its rendered text) as an input — but that integration is Phase 05's to design, when Phase 05 is specified, not something this phase builds ahead of time. This was confirmed by the project owner as the resolved scope for Phase 03 (see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md)).

No existing table, model, service, or frontend feature is modified by this phase.

## 5. Explicitly out of scope

- **Executing a prompt against any real LLM provider.** No outbound network calls, no provider SDK, no API-key storage or Vault/Secrets integration, in this phase. This is the single biggest scope decision in this spec — confirmed with the project owner rather than assumed, because `03_ARCHITECTURE.md` §3–4, `02_ROADMAP.md` §4, and `08_DEFINITION_OF_DONE.md` §4 all independently flag it as an open question that a session should stop and ask about per [`09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §6, rather than a routine implementation detail. Consequences of this decision: no new entry in [`06_TECH_STACK.md`](../../06_TECH_STACK.md) §1/§2 this phase, no security review trigger under [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.2/§1.6, and no overlap with whatever Phase 05 (Model Playground) eventually specifies for actual provider execution. "Testing" a prompt in this phase means previewing its rendered, substituted text — not sending it anywhere.
- **A separate, first-class "Template" entity distinct from "Prompt."** Every saved prompt is already reusable via Duplicate (requirement 10) — a dedicated template gallery/category system is a speculative abstraction this phase doesn't need, per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) (avoid designing for hypothetical future requirements).
- **Folders or nested organization.** Tags plus search cover the organizational need at this phase's expected scale (a single developer's personal prompt library), consistent with Notes' flat-board and Secrets' flat-list precedent. Folders are a candidate for a future phase if real usage demonstrates the need.
- **Server-side pagination on the list endpoint.** Matches the pre-existing, already-tracked gap in [`02_ROADMAP.md`](../../02_ROADMAP.md) §5 ("list-endpoint pagination") shared by every other list endpoint in the app today (Secrets, Notes, Documents, Project Init history) — not something this phase silently fixes for itself while leaving every sibling feature behind.
- **Import/export of prompts as standalone files, or sharing/collaboration features.** Forge is single-tenant per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.1; there is no second user to share with, and a file-based import/export format is a real, separately-scoped feature (schema versioning, format compatibility) that isn't required for the core authoring/versioning workflow this phase delivers.
- **A rich-text or Markdown-rendered body editor.** The body is plain text edited in Monaco with plain-text/Markdown syntax highlighting (for readability only, not for interpreting the prompt as document structure) — Prompt Studio is not a Documents-style rich-text editor, and does not reuse or modify `features/documents/`.
- **Variable types beyond string/number/boolean** (e.g. arrays, nested objects, file uploads). LLM prompt variables are overwhelmingly scalar substitutions in practice; a structured/nested variable system is unneeded complexity for this phase's scope and can be added later against real demand.
- **Workbench panel or pinned-tool registration.** Phase 01 is released and frozen (`v0.1.0-workbench`). This phase adds only a nav-registry entry (sidebar + command palette reachability), matching Phase 02's precedent exactly.
- **Any relationship to Forge's own future Phase 06 "Projects" entity.** Prompts are not scoped to a project in this phase; that association, if ever added, is Phase 06's or a later phase's decision.
- **Any templating capability beyond flat variable substitution** — conditionals, loops, function calls, filters, includes, or imports inside a prompt body. This is the explicit rendering-determinism constraint in §3.16, added at the project owner's request during specification review: Prompt Studio is deliberately not a general-purpose templating engine, and never becomes one via incremental feature addition to the renderer.

## 6. Open questions

None. The one open question flagged across `02_ROADMAP.md`, `03_ARCHITECTURE.md`, and `08_DEFINITION_OF_DONE.md` (whether Prompt Studio should include live LLM execution, and how it sequences against Phase 05) was raised to the project owner directly during this specification session and resolved as documented in §4–§5 above — see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md) for the record of that exchange.

The two smaller items previously listed here were confirmed by the project owner during specification review (2026-07-22) and are no longer open:

- [x] `${name}` placeholder syntax (Python `string.Template` default) — **approved as-is**. `{{name}}` (Handlebars/Jinja-style) is explicitly rejected: "there is no compelling reason to support two syntaxes."
- [x] 50 variables and 20,000 characters as prompt body ceilings — **approved as-is**, "generous while remaining practical," may be raised later without a breaking change.

## 7. TODO

- [x] Project-owner sign-off recorded 2026-07-22 — **Approved** (see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md)). `IMPLEMENT.md` is updated to reflect Stage 2 (Technical Planning) Authorized; Stage 3 (Implementation) begins once [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)'s milestone plan is complete.

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
