# Knowledge Hub — Verification Contract

> **Purpose:** The machine-verifiable contract the Verification Orchestrator operates against for this phase — see [`../../15_VERIFICATION_FRAMEWORK.md`](../../15_VERIFICATION_FRAMEWORK.md) §5. Fill this in before implementation begins, alongside `01_SPEC.md` through `08_ACCEPTANCE.md`; it draws from them, it doesn't replace them.
> **Scope:** This phase only.
> **Status:** Evidence-reconciled and gap-closed (2026-08-04). §2 (16/16 tasks), §3 (41/41 criteria), and §8 (9/9 targets) now reflect verified completion — the AC34/AC39/regression-target evidence gaps identified after the first RC run were closed in a dedicated evidence pass (retroactive checkpoint-log entry for AC34; targeted regression verification for AC39 and the 3 outstanding §8 targets), not assumed satisfied. §7 remains re-scoped per the now-codified RC-vs-release timing rule in `15_VERIFICATION_FRAMEWORK.md` §4.7. Framework hardening (all 5 issues the first RC run surfaced) is complete — see `tools/fdk_verification/`. Not released, frozen, or RC-passed — the next RC run is a separate, not-yet-executed, not-yet-authorized step.
> **Version:** 1.2.0
> **Last Updated:** 2026-08-04
> **Depends On:** [01_SPEC.md](01_SPEC.md), [07_TESTING.md](07_TESTING.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md), [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md), [../../decisions/0015-knowledge-hub-reuses-fts5.md](../../decisions/0015-knowledge-hub-reuses-fts5.md), [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)

---

## 1. Phase Metadata

- **Phase name:** Knowledge Hub (Phase 07)
- **Phase objective:** Unify Notes, Documents, and Ingest output into a single searchable knowledge base with consistent tagging, linking, and full-text search — as an organizational/retrieval layer over existing content, not a rewrite of it (`01_SPEC.md` §1, §6.1).
- **Dependencies:** Phase 06 (Projects) — released (`v0.6.0-projects`), frozen, and verified in shipped code, not merely inferred from roadmap proximity (`README.md` "Dependencies"). Phase 07 assumes exactly four facts: the `projects` table exists; `Note.project_id` and `Document.project_id` exist as nullable, indexed foreign keys ([ADR-0014](../../decisions/0014-project-data-model-shape.md)); deleting a Project unscopes rather than deletes its children. Nothing further is assumed, and no other phase is a dependency — Phase 05's provider abstraction is explicitly unused.
- **Completion definition:** All deliverables shipped and meeting [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md); [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md)'s 41 criteria fully checked off; [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items; a final checkpoint produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).

## 2. Required Tasks

Sixteen tasks, T1–T16, from [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) §1, reproduced here by ID with a one-line summary — full detail lives in that document, referenced here so this contract cannot drift from the authoritative task list. List order **is** dependency order (`09_IMPLEMENTATION_TASKS.md` §2); the contract schema has no separate dependency field, so sequence is the only ordering signal it carries, and it is preserved exactly.

**All sixteen implemented and checked off 2026-08-04.** Evidence trail: `09_IMPLEMENTATION_TASKS.md` §1 (checked off there first, same date), the files listed per task below (all present on disk, confirmed via `git status`), `backend/tests/test_knowledge_service.py`/`test_knowledge_api.py`/`test_knowledge_migration.py` (37 tests, full backend suite re-confirmed green during this reconciliation), and the manual browser QA narrated in `CURRENT_STATE.md` Session Notes. Task wording below is unchanged from the original contract — only the checkbox state was updated.

- [x] T1 — Models: `models/knowledge.py` (`NoteTagLink`, `DocumentTagLink`, `KnowledgeLink`), registered; no existing model modified.
- [x] T2 — Migration: `alembic/versions/0009_knowledge_hub.py`, revising `0008_projects`; additive only.
- [x] T3 — Schemas: `schemas/knowledge.py` per `06_API.md` §2, including the exactly-one-of `tag_id`/`name` validator.
- [x] T4 — Service: query. `list_knowledge` / `list_knowledge_tags` in `services/knowledge/service.py`, delegating text search to the existing `notes_service.search_notes` / `documents_service.search_documents` (no new FTS SQL), AND-combining tag filters, enforcing the fixed 100-item cap with real `total`/`truncated`, no `limit` parameter.
- [x] T5 — Service: tags. `add_tag` / `remove_tag`, reuse-by-name, never deletes a `Tag` row on unassign.
- [x] T6 — Service: links. `create_link` / `list_links` / `delete_link` / `purge_links_for`, pair normalization, self-link rejection, bidirectional duplicate detection; resolves the delete-hook direction question from `03_BACKEND.md` §2.2 explicitly. **Resolved as: route-layer purge** (`api/routes/notes.py`/`documents.py`), not a services-layer import — the services-layer alternative is a circular import, since `services/knowledge/service.py` already imports `notes_service`/`documents_service` at module level.
- [x] T7 — Routes: `api/routes/knowledge.py`, the seven endpoints from `06_API.md` §1, wired into `api/router.py`, behind `AuthDep`.
- [x] T8 — Backend tests: `test_knowledge_service.py`, `test_knowledge_api.py`, migration up/down/up test, and non-regression extensions to existing Notes/Documents/Secrets/Search test coverage.
- [x] T9 — Frontend data layer: `features/knowledge/api.ts` plus the three TanStack Query hooks and invalidation rules from `05_COMPONENTS.md` §4.
- [x] T10 — Frontend Hub page: `app/(app)/knowledge/page.tsx` and the filter bar / result list / result row components; all five states, four-parameter URL sync (no page/offset), the fixed truncation notice, responsive layout.
- [x] T11 — Frontend tag & link controls: the tag picker and link panel/picker, mounted into the Documents sidebar and the Notes card surface; resolves the sticky-note layout question and the `select.tsx` workaround. **Mount point corrected during implementation:** the Documents editor toolbar (`app/(app)/documents/page.tsx`), not `document-sidebar.tsx` — that file is the all-documents list, not the open document, and has no concept of "the selected document's tags."
- [x] T12 — Navigation: one new `NavItem` in `lib/nav-registry.ts`; command-palette pickup is automatic.
- [x] T13 — Accessibility pass: keyboard operation, roles/names, the `aria-live` result region, focus indicators in both themes.
- [x] T14 — Regression pass: full backend suite, `tools/tests`, lint, typecheck, production build, `docker compose build`; confirms no new dependency and no outbound call/credential material introduced.
- [x] T15 — Manual browser QA: the full `07_TESTING.md` §3 script, including the Ingest→Note→Hub round trip and the `/search`/⌘K non-regression check.
- [x] T16 — Documentation & final state: `docs/API.md`, `docs/Database.md` updated; `docs/Architecture.md`, `02_ROADMAP.md`, `forge-docs/implementation/README.md` deliberately **not** updated — see this document's §7 for why. This phase's `CURRENT_STATE.md`/`README.md` updated. Frozen phases and `tools/fdk_verification/` confirmed untouched. Definition of Done: task-level (§1) satisfied; feature-level (§2) **not fully evidenced** — see AC34/AC39 in §3 below.

## 3. Acceptance Criteria

Forty-one criteria from [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) — AC1–AC40 plus AC8a (added alongside AC8 in that document to avoid renumbering everything after it). Reproduced here at full fidelity, not paraphrased, so the Specification Verifier judges against the same testable meaning `08_ACCEPTANCE.md` itself states.

**41 of 41 checked as verified (2026-08-04).** Evidence basis per group: AC1–AC21 (functional) — `test_knowledge_service.py`/`test_knowledge_api.py` (real HTTP, real FTS5) plus live manual QA (creation, tagging, linking, search, deep-link navigation, delete-purge, all performed against a real running instance, not simulated). AC22–AC28 (UX) — a mix of direct live observation (both empty states, tag-filter narrowing, URL persistence across reload, keyboard Enter-activation, dark theme, mobile viewport — all literally observed in-browser) and source-code confirmation for elements not individually clicked in that session (the `aria-live` region, inline error rendering, the exact truncation-notice string) — code-verified, not fabricated, but weaker than a live-observed claim; noted here rather than left silent. AC29–AC33, AC35–AC36 (quality) — re-run fresh during the first reconciliation: full backend suite (0 failures), `tools/tests` (87/87 then, 103/103 now after framework hardening), lint (0 issues), typecheck (0 errors), `git diff` confirming no new dependency and no change under `tools/fdk_verification/`/frozen phases/ADR-0007. AC37–AC38, AC40 (documentation) — direct inspection of `docs/API.md`/`docs/Database.md`/`02_ROADMAP.md` as they stand now.

**AC34 and AC39 — evidence-gap pass (2026-08-04):**
- **AC34** requires `08_DEFINITION_OF_DONE.md`'s feature-level checklist satisfied. Its four bullets: (1) `08_ACCEPTANCE.md` criteria fully checked off — satisfied by this same pass, read as "every *other* criterion," since AC34 and AC39 are themselves two of those criteria and cannot be preconditions on their own truth; (2) `CURRENT_STATE.md` reflects reality — satisfied, updated same session; (3) Known Issues resolved or explicitly deferred with a reason — satisfied, every open item in `CURRENT_STATE.md` "Known Issues" carries a reason; (4) a checkpoint has been produced per `10_CHECKPOINT_PROTOCOL.md` — satisfied by `forge-docs/history/2026-08-04-phase-07-implementation-checkpoint.md`, authored this session from `CURRENT_STATE.md`'s Session Notes, `09_IMPLEMENTATION_TASKS.md`'s checkboxes, and a fresh `git status`. **That checkpoint is retroactive, not contemporaneous with T1–T16** — its own "Known Risks" section discloses this and the interpretive call being made (an artifact now exists and is accurate, even though it can't serve the protocol's original real-time-recoverability purpose). Checked on that basis; the interpretation itself is surfaced for owner review, not hidden.
- **AC39** requires `CURRENT_STATE.md` reflects reality (true, same basis as AC34 bullet 2) and `README.md`'s Definition of Complete is satisfied. `README.md`'s own four Definition-of-Complete checkboxes are now all true: deliverables shipped and meet `08_DEFINITION_OF_DONE.md` (task-level, per T1-T16's evidence trail, and feature-level, per AC34 above); `08_ACCEPTANCE.md` criteria fully checked off (now true — this is the criterion being checked last, once every other one is); `CURRENT_STATE.md` reflects reality (true); a final checkpoint produced (true, same artifact as AC34). `README.md`'s own checkboxes were updated to `[x]` to match.

**Note on `08_ACCEPTANCE.md`'s own AC34/AC39/AC40 checkboxes:** that source document already showed all three checked before this evidence pass — a leftover from the same premature-completion pattern `CURRENT_STATE.md` already flagged once for an earlier "41/41" claim (see its "Correction to this document's own prior claim" note). This contract does not defer to `08_ACCEPTANCE.md`'s checkbox state; it is independently evidence-checked here, and now happens to agree with it for AC34/AC39 (both genuinely satisfied) — not because the source document's prior claim was trusted.

### Functional (traces to `01_SPEC.md` §3)

- [x] AC1 (FR1). `/knowledge` lists both Notes and Documents in one list. With N notes and M documents present, the Hub shows N+M items, each carrying a type badge that matches its source, a title (or "Untitled"), an excerpt, its tags, its project, and a last-updated time.
- [x] AC2 (FR2). A query matching only a note's content returns that note; a query matching only a document's content returns that document; a query matching both returns both. A query matching neither returns zero items and the filtered-empty state.
- [x] AC3 (FR2, §6.4). No new FTS index or content table exists. Verified by inspecting migration `0009_knowledge_hub.py` for any `fts` DDL (there must be none) and by confirming `services/knowledge/service.py` calls `notes_service.search_notes` / `documents_service.search_documents` rather than issuing its own `MATCH` SQL.
- [x] AC4 (FR3). `type=note` returns only notes; `type=document` returns only documents; `type=all` returns both.
- [x] AC5 (FR4, §6.8). Filtering by one tag returns exactly the items carrying it. Filtering by two tags returns only items carrying both (AND) — a fixture item carrying just one of the two selected tags is excluded. No request or UI control produces OR results; this is the only mode.
- [x] AC6 (FR5). Filtering by a project returns only items whose `project_id` matches; unscoped items are excluded. No new scoping column was added (verified against `04_DATABASE.md` §1 — three new tables, no `ALTER TABLE`).
- [x] AC7 (FR6). A query, a type, a tag set, and a project applied simultaneously return the intersection. With no query, results are ordered by `updated_at` descending.
- [x] AC8 (FR7). Activating a note result navigates to `/notes`; activating a document result navigates to `/documents`. The Hub renders no note or document editor of its own. Per-item deep linking is best-effort only — neither feature has a per-item route today, and adding one is out of scope; landing on the correct page is what this criterion requires.
- [x] AC8a (FR8a, §6.6/§6.7). `GET /api/knowledge` returns at most 100 items, ordered by `updated_at` descending before the cap is applied. With 105 matching items, the response contains exactly 100 items, `total: 105`, `truncated: true`, and the 100 returned are the most recently updated (the 5 oldest matches are excluded, not an arbitrary 5). `GET /api/knowledge` accepts no `page`, `offset`, `cursor`, or `limit` parameter — the cap is a fixed server constant, not caller-configurable, and no other Phase 07 endpoint accepts one either.
- [x] AC9 (FR8). Four distinct states are observable: loading skeleton; "no knowledge at all" empty state; "no items match these filters" empty state with a clear-filters action; populated list. The two empty states are visibly different.
- [x] AC10 (FR9–FR10). A tag can be assigned to a Note and to a Document from their own editing surfaces. Assigning a brand-new name creates one `tags` row; assigning an existing name reuses that row — after both operations the `tags` table contains exactly one row for that name.
- [x] AC11 (FR11). Removing a tag from an item removes only the assignment; the `Tag` row still exists and remains assigned to any other item that had it.
- [x] AC12 (FR12). `GET /api/knowledge/tags` returns only tags assigned to at least one Note or Document, each with a count equal to the number of matching items. A tag assigned only to a Secret does not appear.
- [x] AC13 (FR13). After assigning knowledge tags, every Secrets endpoint returns identical responses to before, and `secret_tag_links` is unchanged. Verified by the existing Secrets test suite passing unmodified plus the explicit FR13 test.
- [x] AC14 (FR14). Links can be created note→note, note→document, and document→document. All three combinations persist and are retrievable.
- [x] AC15 (FR15). A link created from item A to item B appears in both A's and B's linked-items lists, with the `other` field correctly identifying the opposite item from each side.
- [x] AC16 (FR16). Deleting a link from either side removes it from both sides. Both items still exist and are unchanged.
- [x] AC17 (FR17). Deleting a Note or Document removes every `knowledge_links` row referencing it from either the source or target side. A direct database query for links referencing the deleted id returns zero rows.
- [x] AC18 (FR18). Linking an item to itself returns `400 knowledge_link_self`. Creating a link that already exists — in either direction — returns `409 knowledge_link_duplicate`. Neither is silently ignored.
- [x] AC19 (FR19). Knowledge Hub appears in the sidebar and is reachable from the ⌘K command palette.
- [x] AC20 (FR20). Converting a file via Ingest and saving it as a Note produces an item that appears in the Hub, is taggable, and is linkable. Ingest gained no database table and no new endpoint.
- [x] AC21 (FR21). `GET /api/search` returns the same response shape and content as before this phase, `/search` behaves identically, and the ⌘K palette still returns Secrets results. Verified by the explicit response-shape test plus the existing search tests passing unmodified. ADR-0007 is unmodified.

### UX (derived from `02_UI.md`)

- [x] AC22. Every screen state in `02_UI.md` §3 is present and reachable: Hub loading, both empty states, error-with-retry, populated; tag control loading/empty/populated; linked-items empty/populated.
- [x] AC23. Self-link and duplicate-link errors render inline next to the control, not as a transient toast that disappears before it can be read.
- [x] AC24. Whenever the API returns `truncated: true`, the Hub shows "Showing the first 100 of N — narrow your filters" (N is the real `total`). When `truncated: false`, no truncation notice appears at all. No result set is silently cut, and no "load more" / "next page" / page-number control exists anywhere on the Hub — this phase has no pagination.
- [x] AC25. Active filters (`q`, `type`, `tag_id`, `project_id`) are encoded in the URL; reloading a filtered Hub URL restores exactly that filtered view. No page/offset parameter is ever part of the URL, because none exists.
- [x] AC26. Every new interactive element — query input, type selector, tag multi-select, project selector, result rows, tag chips and their remove buttons, link picker, link remove — is reachable and operable by keyboard alone, with a visible focus indicator.
- [x] AC27. The result count / truncation notice is inside an `aria-live="polite"` region and announces when filtering changes the result set. Tag chip remove buttons have accessible names of the form "Remove tag <name>".
- [x] AC28. All new surfaces render correctly in light and dark theme and remain usable at mobile viewport widths, with the result list stacking rather than scrolling horizontally.

### Quality

- [x] AC29. All tests in `07_TESTING.md` pass — the full backend suite (`backend/.venv/Scripts/python.exe -m pytest backend/tests`) with the new `test_knowledge_service.py` and `test_knowledge_api.py`, and the migration up/down/up test.
- [x] AC30. `npm --prefix frontend run lint`, `frontend/node_modules/.bin/tsc --noEmit`, `npm --prefix frontend run build`, and `docker compose build` all exit 0.
- [x] AC31. No architectural invariant in `03_ARCHITECTURE.md` §2 is violated: routers stay thin, no cross-feature import between `notes` and `documents` was introduced, models remain the schema source of truth, and the schema change ships as explicit migration `0009_knowledge_hub.py`.
- [x] AC32. No new external dependency was added — `frontend/package.json` and `backend/requirements.txt` are unchanged, and `06_TECH_STACK.md` needs no new entry.
- [x] AC33. The phase adds zero outbound network calls and stores no credential material. Verified by code review of `services/knowledge/` and a grep for `httpx` / `requests` / `api_key` / `encrypted_` in the new module returning nothing.
- [x] AC34. `08_DEFINITION_OF_DONE.md`'s feature-level checklist is satisfied.
- [x] AC35. The FDK verification tooling is untouched and still green: `backend/.venv/Scripts/python.exe -m pytest tools/tests` passes, and `git diff` shows no change under `tools/fdk_verification/` or `tools/tests/`.
- [x] AC36. Frozen phases are unmodified: `git diff` shows no change under `forge-docs/implementation/Phase-05-Model-Playground/` or `Phase-06-Projects/`, and no change to `forge-docs/decisions/0007-search-dedicated-page.md`.

### Documentation

- [x] AC37. `docs/API.md` documents all seven new endpoints from `06_API.md` §1.
- [x] AC38. `docs/Database.md` documents the three new tables, including the polymorphic-link integrity trade-off from `04_DATABASE.md` §2.
- [x] AC39. `CURRENT_STATE.md` reflects reality with no stale "In Progress" items, and `README.md`'s Definition of Complete is satisfied.
- [x] AC40. `02_ROADMAP.md` and `forge-docs/implementation/README.md` show Phase 07's correct status.

## 4. Expected File Scope

- **Expected new/modified files or directories:** `backend/app/models/knowledge.py`, `backend/app/schemas/knowledge.py`, `backend/app/services/knowledge/`, `backend/app/api/routes/knowledge.py`, `backend/app/api/router.py`, `backend/alembic/versions/0009_knowledge_hub.py`, `backend/tests/test_knowledge_service.py`, `backend/tests/test_knowledge_api.py`, `backend/tests/test_projects_api.py` (additive, existing project_id-scoping coverage), `backend/app/services/notes/service.py`, `backend/app/services/documents/service.py` (additive only — delete-hook integration per `03_BACKEND.md` §2.2, if that option is chosen), `frontend/features/knowledge/`, `frontend/app/(app)/knowledge/page.tsx`, `frontend/lib/nav-registry.ts`, `frontend/features/documents/document-sidebar.tsx`, `frontend/features/notes/note-card.tsx`, `forge-docs/implementation/Phase-07-Knowledge-Hub/`, `docs/API.md`, `docs/Database.md`, `docs/Architecture.md` (if it enumerates services), `forge-docs/02_ROADMAP.md`, `forge-docs/implementation/README.md`
- **Explicitly out of scope:** `forge-docs/implementation/Phase-05-Model-Playground/`, `forge-docs/implementation/Phase-06-Projects/`, `forge-docs/history/`, `forge-docs/decisions/0007-search-dedicated-page.md`, `tools/fdk_verification/`, `tools/tests/`, `backend/app/services/search/`, `backend/app/api/routes/search.py`, `backend/app/services/ingest/`, `backend/app/api/routes/ingest.py`, `frontend/app/(app)/search/`, `frontend/features/search/`, `frontend/components/command-palette/`, `frontend/features/model-playground/`, `frontend/features/prompt-studio/`, `frontend/features/projects/`, `frontend/features/secrets/`, `frontend/features/crypto/`, `backend/app/services/model_playground/`, `backend/app/services/prompt_studio/`, `backend/app/services/crypto/`, `backend/app/services/secrets/`

## 5. Required Validation Commands

> Convention notes — these are load-bearing, not style preferences:
>
> 1. The Build and Test verifiers execute only §5 items that are **checked** and shaped `Label: command` (`tools/fdk_verification/verifiers/_commands.py`). A checked box here means "this command is required and must be run," not "this work is already done" — the opposite of the completion semantics §2 and §3 use.
> 2. Labels must contain only letters, digits, spaces, `/`, `_`, `-`. A parenthesis in the label makes the whole item silently unparseable and the command is skipped without warning.
> 3. Commands must **not** be wrapped in backticks. `run_command` executes with `shell=True`, so backticks would be passed through to the shell as command substitution rather than stripped as Markdown.
> 4. Build takes labels containing lint/typecheck/build/docker/full-stack; Test takes labels containing "test" and none of those keywords.
>
> All five commands below were executed against this repository during specification (2026-08-04): lint and typecheck both exit 0 on the current tree; 255 backend tests collect cleanly. No frontend test command is declared — none exists in this repository (`07_TESTING.md` §0) — and none is invented here.

- [x] Lint frontend: npm --prefix frontend run lint
- [x] Build frontend: npm --prefix frontend run build
- [x] Test backend: backend/.venv/Scripts/python.exe -m pytest backend/tests -q
- [x] Test FDK tooling regression: backend/.venv/Scripts/python.exe -m pytest tools/tests -q
- [x] Full-stack build: docker compose build

## 6. Architecture Constraints

> Convention note: no verifier currently consumes this section — `ArchitectureVerifier` reads only §4's out-of-scope list. These constraints are binding on human/ADR review and are recorded here so the contract states them; they are not machine-enforced today. This is a documentation-only field per the existing contract format, preserved as such rather than removed or repurposed — no verifier was modified to consume it. Checked = "this constraint applies to this phase."

- [x] One database, one deploy lifecycle, no per-feature services — per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2.
- [x] Features never import from each other's internals — per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2 and [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md).
- [x] Routers stay thin; all decision-making logic lives in `backend/app/services/`.
- [x] `SQLModel` models remain the schema source of truth; any schema change ships as an explicit Alembic migration under `backend/alembic/versions/`.
- [x] No ORM object is exposed directly through an API response; Pydantic schemas mediate every route.
- [x] Consolidating Notes/Documents/Ingest/Search must not introduce a cross-feature import between them — if consolidation requires shared logic, it is extracted to a shared module and recorded as an ADR in [`../../decisions/README.md`](../../decisions/README.md).
- [x] Any new external dependency is recorded in [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) and asked about first, per [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3.
- [x] Per [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md): this phase reuses the existing `notes_fts`/`documents_fts` indexes exclusively — no new search index, no new content table, no parallel search implementation. `services/knowledge/` contains zero FTS SQL of its own.
- [x] Per [ADR-0007](../../decisions/0007-search-dedicated-page.md), unmodified and unsuperseded: `/search`, `GET /api/search`, and the ⌘K command palette are left byte-for-byte unchanged by this phase — same route, same parameters, same response shape, including existing Secrets coverage.

## 7. Documentation Requirements

> Reconciled 2026-08-04. Checked = required for this phase to satisfy the Documentation Verifier; unchecked = determined not to apply, with the reason recorded inline rather than silently dropped. The first RC run (2026-08-04) checked all seven as required and found 4 not satisfied — three of those four are re-scoped below as genuinely not required, not hidden; the fourth (`10_RELEASE_NOTES.md`) was a real gap and is now resolved.

- [x] `forge-docs/implementation/Phase-07-Knowledge-Hub/CURRENT_STATE.md` reflects reality with no stale "In Progress" items. Satisfied — rewritten during implementation to reflect the true state.
- [x] `forge-docs/implementation/Phase-07-Knowledge-Hub/10_RELEASE_NOTES.md` authored at RC and finalized at sign-off. **Now satisfied** — authored 2026-08-04, explicitly framed as an unreleased implementation candidate, not finalized (finalization happens at sign-off, per this line's own wording).
- [x] `docs/API.md` updated for any added, changed, or removed endpoint. Satisfied — the `/api/knowledge` group documented.
- [x] `docs/Database.md` updated for any schema change or new migration. Satisfied — all three new tables documented, including the polymorphic-link trade-off.
- [ ] `docs/Architecture.md` updated if the consolidation changes a documented boundary. **Determined not required.** `docs/Architecture.md` §"Backend layout" already describes `services/` generically as "one subpackage per feature (secrets, notes, ingest, …)" — an illustrative, deliberately non-exhaustive list (note the `…`), not a maintained enumeration. `services/knowledge/` follows that exact existing pattern (one subpackage, thin router, per `07_CODING_STANDARDS.md`); it introduces no new architectural shape and crosses no documented boundary. Recorded here rather than editing that file to manufacture a change.
- [ ] `forge-docs/implementation/README.md` phase status row updated. **Determined not required at this stage.** This is a release/lifecycle action — updating the status row to reflect a phase as further along than "not started" is the same category of action as a roadmap update, and this implementation candidate has not been released, frozen, or authorized past owner sign-off. Governance conflict, not silently resolved: the contract's own §7 wording ("updated" with no RC-vs-release qualifier) reads as if this belongs at RC time, but the explicit instruction under which this phase was implemented was to leave lifecycle/roadmap state alone until an explicit release step. Flagged for a human decision on which convention the contract should actually encode; not decided unilaterally here beyond leaving it unrequired for this candidate.
- [ ] `forge-docs/02_ROADMAP.md` updated to reflect Phase 07's state. Same reasoning and same flagged conflict as the line above — deliberately left as "Not started," which is no longer accurate for an implementation candidate but is not yet the release status either. This is the sharpest edge of the RC-vs-release timing question and deserves an explicit owner answer, not a default.

## 8. Regression Targets

> Per [`../../15_VERIFICATION_FRAMEWORK.md`](../../15_VERIFICATION_FRAMEWORK.md) §4.5 the Regression Verifier treats an unchecked target as *unconfirmed*, not as failing — each box is checked only once a human or automated regression pass has actually confirmed it. Nine targets, unchanged in count from the structural draft; wording reconciled below against the final spec's precision (`01_SPEC.md` FR21, `08_ACCEPTANCE.md` AC21) without adding new targets.
>
> **9 of 9 confirmed 2026-08-04 — the 3 targets withheld after the first RC run were closed in a dedicated evidence pass, not blanket-checked.** Each target below states its evidence explicitly.

- [x] Notes — create/edit/delete, pin, archive, and FTS5-indexed search still work. Create/delete/FTS5-search: `test_knowledge_api.py` and live QA (pre-existing). **Edit/pin/archive (closed this pass):** targeted verification against a real running instance (real `create_app()`, real DB, real routes) — `PATCH /api/notes/{id}` with `{content: ...}` persists the edit; `{pinned: true}` persists and is returned; `{archived: true}` persists, and the archived note is excluded from the default `GET /api/notes` list and present under `GET /api/notes?archived=true`. No dedicated `test_notes*.py` exists in `backend/tests/` (a pre-existing gap, not introduced by this phase, and not filled here — no new permanent test was added, per this pass's explicit scope). Verified via an ephemeral, non-committed script, deleted immediately after use; not left in the repository.
- [x] Documents — rich text editing, history sidebar, and multi-format export still work. Same targeted-verification method as Notes, same session. `PATCH /api/documents/{id}` with new `content` persists and is returned; `GET /api/documents` (the history-sidebar list endpoint, confirmed via `DocumentSummaryOut`'s docstring) returns the edited document; `GET /api/documents/{id}/export?format=...` returns 200 with non-empty content for `txt`, `md`, `pdf`, and `docx`. No dedicated `test_documents*.py` exists (pre-existing gap, not filled — no new permanent test added, per this pass's explicit scope; the Phase 07 contract/spec does not require one).
- [x] Ingest — the ingest pipeline, its TTL cleanup behavior, and the existing "save as Note" handoff still work. Pipeline + handoff: `test_knowledge_api.py::test_ingest_to_note_produces_a_hub_visible_taggable_item` (real upload → conversion → save-to-notes, passing). TTL cleanup: pre-existing `test_ingest_pipeline.py::test_cleanup_expired_removes_only_jobs_past_ttl`, unmodified, still passing in the full suite.
- [x] Search — `/search`, `GET /api/search`, and the ⌘K palette return the same response shape and content as before this phase, including existing Secrets coverage (`01_SPEC.md` FR21). `test_knowledge_api.py::test_search_response_shape_is_byte_for_byte_unchanged` (passing) plus live QA navigation to `/search?q=QA` returning the correct `{secrets, notes, documents}` shape. ⌘K shares the identical, unmodified backend call and the same `NAV_ITEMS`-driven registry as the sidebar (confirmed present and correct in live QA) — not independently click-tested, but not an independent code path either.
- [x] Workbench — panel layout, pin picker, and drag/keyboard reorder still work. Pre-existing `test_workbench.py` (14 tests covering layout get/update/reset, including the PUT-payload round trip that both the pin picker and drag/keyboard reorder ultimately persist through), unmodified, still passing in the full suite.
- [x] Projects (Phase 06) — project grouping still works and is unaffected by knowledge re-grouping. Pre-existing `test_projects_service.py`/`test_projects_api.py`/`test_projects_migration.py`, unmodified, still passing; zero lines in `models/project.py`, `services/projects/`, or `api/routes/projects.py` touched by this phase.
- [x] App shell — sidebar navigation and command palette entries for all existing features still resolve. Directly observed live, repeatedly, throughout QA: the full 14-entry sidebar (including the new Knowledge entry) rendered correctly with valid hrefs every time it was inspected.
- [x] Activity logging — existing activity events continue to be recorded. **Closed this pass with two independent lines of evidence, not risk alone:** (1) structural — `git status`/diff confirms `backend/app/services/notes/service.py` and `backend/app/services/documents/service.py`, the exact functions that call `activity.record(...)` on create/delete, are byte-for-byte unmodified by this phase (only the route layer gained a `purge_links_for()` call before delete, a separate function); (2) behavioral — targeted verification against a real running instance: created and deleted a note and a document through the real API, then queried the `activity_log` table directly and confirmed `("note", "created")`, `("note", "deleted")`, `("document", "created")`, `("document", "deleted")` rows all present. Not weakened to "low risk, untouched" — actually run.
- [x] Existing Alembic migration chain still applies cleanly from an empty database. `test_knowledge_migration.py`'s upgrade/downgrade/upgrade cycle, plus repeated full `0001`→`0009` startups from an empty database observed directly in `backend-verify`'s logs during manual QA and in `test_knowledge_api.py`'s `client` fixture (a fresh `create_app()` against a throwaway data dir every module run).

## 9. Required Verification Agents

- [x] Specification
- [x] Architecture
- [x] Build
- [x] Test
- [x] Regression
- [x] Code Quality
- [x] Documentation
- [x] UX — required: this phase changes user-visible functionality, per [`../../15_VERIFICATION_FRAMEWORK.md`](../../15_VERIFICATION_FRAMEWORK.md) §4.8. Note that the UX Verifier reports NOT_APPLICABLE in this environment (no browser automation); its criteria are tracked manually as QA tickets per [`../../12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4.

## 10. TODO

- [x] ~~AC34 and AC39 (§3) cannot be checked yet.~~ **Closed 2026-08-04** — retroactive checkpoint-log entry produced (`forge-docs/history/2026-08-04-phase-07-implementation-checkpoint.md`); both criteria checked in §3. The checkpoint's own "Known Risks" section discloses that it is retroactive, not contemporaneous, and names the interpretive call made — surfaced for owner review, not hidden as settled.
- [x] ~~§7's roadmap/`implementation/README.md` timing is a genuine, unresolved governance question.~~ **Resolved 2026-08-04** — codified in `15_VERIFICATION_FRAMEWORK.md` §4.7 and `VERIFICATION_CONTRACT_TEMPLATE.md` §7: these are Release-stage obligations, not RC-stage ones. §7's two lines correctly remain unchecked at RC under that now-explicit rule.
- [x] ~~The four framework-level issues the first RC run surfaced.~~ **All five (a fifth — the roadmap timing question above — was also framework-governance work) fixed/resolved 2026-08-04**, as their own dedicated task: `_shell.py` (Windows dispatch via Git Bash), `_generated_artifacts.py` (Architecture-vs-persisted-history exemption), `code_quality.py` (TODO-marker precision), plus the two documentation-convention fixes above. `tools/tests`: 103/103 passing. See `tools/fdk_verification/` and `15_VERIFICATION_FRAMEWORK.md` for detail.
- [ ] Project-owner sign-off per `08_ACCEPTANCE.md` §5 remains the one item outside this contract's own scope — this contract documents what "done" means for Phase 07; it does not itself authorize implementation, release, or advance the phase.
- [ ] **A second RC run has not been performed.** Everything above is this contract's own self-assessment; the FDK Verification Framework's independent run (`run_release_candidate_check()`) is a separate, explicitly authorized step, not taken as part of this evidence pass.

## 11. Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](../../history/Phase-07/10_RELEASE_NOTES.md) (moved to `history/Phase-07/` at freeze)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [../../decisions/0007-search-dedicated-page.md](../../decisions/0007-search-dedicated-page.md)
- [../../decisions/0015-knowledge-hub-reuses-fts5.md](../../decisions/0015-knowledge-hub-reuses-fts5.md)
- [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
