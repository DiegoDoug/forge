# Knowledge Hub — README

> **Purpose:** Entry point for the Knowledge Hub phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04; §7's four open questions resolved 2026-08-04)
> **Status:** 🔒 Released & frozen — `v0.7.0-knowledge-hub` (commit `b445b09`), bug fixes only from here. See [`CURRENT_STATE.md`](CURRENT_STATE.md) for the full history and [`../../history/Phase-07/`](../../history/Phase-07/) for the archived release notes and post-implementation review.
> **Last Updated:** 2026-08-05

---

## Objective

Unify Notes, Documents, and Ingest output into a single searchable knowledge base with consistent tagging, linking, and full-text search.

## Scope

**In scope:**

- [ ] A dedicated Knowledge Hub page at `/knowledge` listing Notes and Documents together, with full-text query plus type, tag, and project filters.
- [ ] Tagging for Notes and Documents, using the existing shared `tags` vocabulary.
- [ ] Explicit links between knowledge items (note↔note, note↔document, document↔document), visible from both sides.
- [ ] A `services/knowledge/` backend composition layer and seven endpoints under `/api/knowledge`.
- [ ] Three additive tables and one additive migration.
- [ ] Sidebar and command-palette reachability.

**Out of scope:** see [`01_SPEC.md`](01_SPEC.md) §5 for the full list with reasoning. The headline exclusions are Secrets as Hub content, wiki-style `[[title]]` link parsing, a new search index, **pagination** (final decision, not a placeholder — see [`01_SPEC.md`](01_SPEC.md) §6.7), editing content inside the Hub, changes to the Documents export pipeline, and any AI/semantic-search capability. In place of pagination, results are capped at a fixed 100 items with explicit truncation reporting ([`01_SPEC.md`](01_SPEC.md) §6.6).

## Relationship to the shipped application

The Hub **unifies access to** the existing Notes, Documents, and Ingest features — it does not rewrite them. Notes stay on the Notes board, Documents stay in the Documents editor, Ingest stays a transient conversion pipeline whose output enters the knowledge base through its already-shipped "save as Note" path. The existing `/search` page and ⌘K palette are deliberately untouched, per [ADR-0007](../../decisions/0007-search-dedicated-page.md).

This relationship is **confirmed**, not inferred — the earlier scaffold flagged it as the Lead Architect's unratified proposal; it was settled with the project owner on 2026-08-04 and recorded in [`01_SPEC.md`](01_SPEC.md) §4 and §6.

Actual current code paths (the earlier scaffold listed `backend/app/notes/` and similar, which do not exist):

- Related frontend: `frontend/features/notes/`, `frontend/features/documents/`, `frontend/features/ingest/`, `frontend/features/search/`
- Related backend: `backend/app/services/notes/`, `backend/app/services/documents/`, `backend/app/services/ingest/`, `backend/app/services/search/`

## Deliverables

- [ ] `backend/app/models/knowledge.py` — three link/join models.
- [ ] `backend/alembic/versions/0009_knowledge_hub.py` — one additive migration.
- [ ] `backend/app/schemas/knowledge.py`, `backend/app/services/knowledge/service.py`, `backend/app/api/routes/knowledge.py`.
- [ ] `backend/tests/test_knowledge_service.py`, `backend/tests/test_knowledge_api.py`, plus a migration up/down/up test and non-regression additions to existing suites.
- [ ] `frontend/features/knowledge/` — `api.ts` and six components.
- [ ] `frontend/app/(app)/knowledge/page.tsx` and one `NAV_ITEMS` entry.
- [ ] Tag and link controls mounted into the Documents sidebar and the Notes card surface.
- [ ] Documentation updates: `docs/API.md`, `docs/Database.md`, `02_ROADMAP.md`, `../README.md`.

## Dependencies

**Phase 06 (Projects) — satisfied and verified, not assumed.**

The earlier scaffold said "Likely depends on Phase 06 — TODO: confirm ordering," and `02_ROADMAP.md` §3 warns that its relationship column is inference rather than a ratified decision. That ambiguity is now resolved by inspection of shipped code rather than by proximity in the roadmap:

- Phase 06 is released (`v0.6.0-projects`, commit `ddc8972`) and frozen.
- `projects` exists as a top-level table.
- `Note.project_id` and `Document.project_id` exist as nullable, indexed foreign keys, per [ADR-0014](../../decisions/0014-project-data-model-shape.md).
- Deleting a Project unscopes rather than deletes its children.

Phase 07 may assume **exactly those four facts** and nothing further. It reads `project_id` and never writes it, adds no column, and changes no project semantics. Phase 06's deferred items (multi-project membership, nested projects, Prompt Studio scoping) remain deferred and are not prerequisites.

No other phase is a dependency. Phase 05's provider abstraction is explicitly unused — this phase makes no outbound calls.

## Milestones

- [ ] **Milestone 1 — Backend foundation (T1–T3).** Models, migration, schemas. Complete when the migration applies cleanly up/down/up and the schema layer typechecks.
- [ ] **Milestone 2 — Backend behavior (T4–T8).** Query, tagging, linking, routes, and the full backend test suite green.
- [ ] **Milestone 3 — Frontend (T9–T13).** Data layer, Hub page, tag/link controls, navigation, accessibility pass.
- [ ] **Milestone 4 — Release candidate (T14–T16).** Regression pass, manual QA, documentation, final state.

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

**Technical**

- [ ] The polymorphic `knowledge_links` table cannot use foreign keys, so orphan prevention is service-enforced. Mitigated by AC17 and a dedicated test; recorded in [`04_DATABASE.md`](04_DATABASE.md) §2.
- [ ] The delete-hook direction (`03_BACKEND.md` §2.2) could introduce a feature→composition-layer import that reads as a cross-feature dependency. Resolved deliberately at T6, with a documented fallback.
- [ ] Merging two result sets (notes + documents) in application code rather than one SQL query means sorting and capping happen after the merge, not in the database. Resolved by specification, not left as a risk to implementation: sort by `updated_at DESC` first, apply the fixed 100-item cap second, so the cap always drops the oldest tail (`01_SPEC.md` §6.6). Mitigated by the explicit `total`/`truncated` reporting in `06_API.md` §1.1a and the AC8a test.

**Product / UX**

- [ ] Where tag and link controls fit on a free-positioned sticky-note card is an unsolved design question (`02_UI.md` §1.2), with a popover fallback.
- [ ] Two adjacent surfaces (`/search` and `/knowledge`) may confuse users. Mitigated by keeping their jobs distinct; flagged for review at T15.
- [ ] The shared `select.tsx` label-rendering characteristic will affect three new pickers (`02_UI.md` §5).

**Risks to existing features**

- [ ] Secrets shares the `tags` table — the highest-risk neighbor. Mitigated by AC13 and by adding no column to `secret_tag_links`.
- [ ] `/search` and ⌘K must be provably unchanged (AC21).
- [ ] No frontend test framework exists, so UI regressions can only be caught by typecheck, lint, build, and manual QA (`07_TESTING.md` §0). This is an accepted, documented limitation.

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off. Verified against `VERIFICATION_CONTRACT.md` §3 (41/41, evidence-cited), not `08_ACCEPTANCE.md`'s own checkbox state alone — see that contract's note on the two documents' independent evidence trails.
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md). [`forge-docs/history/2026-08-04-phase-07-implementation-checkpoint.md`](../../history/2026-08-04-phase-07-implementation-checkpoint.md) — authored retroactively; see that document's "Known Risks" for the disclosed interpretive call.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../decisions/0015-knowledge-hub-reuses-fts5.md](../../decisions/0015-knowledge-hub-reuses-fts5.md)
