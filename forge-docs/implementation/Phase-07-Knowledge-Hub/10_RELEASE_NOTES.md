# Knowledge Hub — Release Notes

> **Purpose:** The release-facing summary of this phase — what shipped, what broke on purpose, what to do before upgrading. Not a duplicate of `CURRENT_STATE.md` (the day-to-day working log) — this is the document a user or another engineer reads to understand what changed, not how it was built.
> **Scope:** This phase only.
> **Status:** Draft — RC-passed (third run, 2026-08-05) and owner-signed-off (`08_ACCEPTANCE.md` §5, 2026-08-05), but **not released, tagged, or frozen**. This document is written per `10_CHECKPOINT_PROTOCOL.md`/contract §7's "authored at RC, finalized at sign-off" convention, ahead of the actual release decision. No tag exists yet; do not read this as confirmation of release.
> **Version:** Untagged — no release version has been assigned.
> **Last Updated:** 2026-08-05
> **Depends On:** [CURRENT_STATE.md](CURRENT_STATE.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md)

---

## New Features

- A new **Knowledge Hub** page (`/knowledge`), reachable from the sidebar and command palette, listing Notes and Documents together in one unified, type-labelled, full-text-searchable view.
- Filtering by item type (all/notes/documents), by one or more tags (AND semantics — an item must carry every selected tag), and by project (reusing Phase 06's existing `project_id` scoping).
- Tagging for Notes and Documents, using the same shared `tags` vocabulary Secrets already uses — assign an existing tag or create one inline; unassigning never deletes the tag itself.
- Explicit links between knowledge items in any combination (note↔note, note↔document, document↔document), visible and manageable from either linked item.
- Ingest's existing "save as Note" handoff (`POST /api/ingest/jobs/{job_id}/files/{file_id}/save-to-notes`) now makes converted files findable, taggable, and linkable through the Hub with no change to Ingest itself.
- New backend: `services/knowledge/` (query composition, tag assignment, link management), 3 new tables (`note_tag_links`, `document_tag_links`, `knowledge_links`), 7 new `/api/knowledge/*` endpoints.
- New frontend: `features/knowledge/` (6 components + data layer), tag/link controls mounted into the Documents editor toolbar and the Notes card.

## Breaking Changes

None. Every change is additive — three new tables, no altered column, no changed existing endpoint. `/search`, `GET /api/search`, and the ⌘K command palette are unchanged (verified byte-for-byte identical response shape).

## Migrations

One new migration: `0009_knowledge_hub.py`, revising `0008_projects`. Creates `note_tag_links`, `document_tag_links` (both referencing the existing `tags` table), and `knowledge_links` (a polymorphic note/document link table — see `docs/Database.md` for the integrity trade-off this requires). Purely additive; no existing table or column touched. Verified via `upgrade → downgrade → upgrade` against a simulated pre-existing database with seeded data, plus repeated full-chain (`0001`→`0009`) startups from an empty database during manual QA.

## Bug Fixes

No pre-existing bugs were found or fixed during this phase. Two design decisions were forced by discoveries made during implementation, not bugs in shipped code:

- The delete-hook that purges a deleted item's knowledge links is implemented at the **route layer** (`api/routes/notes.py`/`documents.py`), not inside `services/notes/`/`services/documents/` as `03_BACKEND.md` had left open — the services-layer alternative is a literal circular import, since `services/knowledge/service.py` already imports `notes_service`/`documents_service` at module level to delegate full-text search.
- Two inaccuracies in this phase's own earlier specification were corrected during implementation: Documents *does* support per-item deep linking (`?open={id}`, confirmed in the existing `app/(app)/documents/page.tsx`) — the spec's claim that "neither feature has a per-item route" was wrong for Documents, only Notes truly lacks one. Ingest's real note-handoff endpoint is `/save-to-notes`, not `/to-note` as `01_SPEC.md` FR20 and `06_API.md` originally named it. Both `01_SPEC.md`/`06_API.md` still carry the old names as of this writing — see Known Issues.

## Known Issues

- **`01_SPEC.md` FR20 and `06_API.md` still name Ingest's handoff endpoint `/to-note`; the real endpoint is `/save-to-notes`.** The implementation and its tests use the real name. This is a documented, deliberate gap (a spec-text correction, not a code defect) rather than a silent inconsistency — tracked here per honest-gaps convention (`01_PRODUCT_PRINCIPLES.md` §1.3) pending a follow-up edit to those two files.
- **No dedicated backend regression test suite exists for core Notes or Documents CRUD/editing** (`test_notes*.py`/`test_documents*.py` do not exist in `backend/tests/`) — a pre-existing gap in this repository, not introduced by this phase. This phase's own tests exercise Notes/Documents only through the paths Knowledge Hub touches (create, delete, FTS5 search); rich-text editing, the Documents history sidebar, and multi-format export were not re-verified by this phase's evidence. See `VERIFICATION_CONTRACT.md` §8 for the precise regression-confirmation state.
- **Resolved.** A checkpoint log entry (`forge-docs/history/2026-08-04-phase-07-implementation-checkpoint.md`, committed as `36d2ffa`) now exists for this phase's implementation session, authored retroactively during evidence reconciliation — its own "Known Risks" section discloses that it was written after the session it describes, not contemporaneously, and names the interpretive call this implies. `08_ACCEPTANCE.md` AC34 and AC39 are checked on that basis.
- **The Notes board's drag-wrapped controls and Base UI's `Popover` trigger require a full native pointer-event sequence to activate under this session's browser-automation tooling** — a tooling limitation encountered during manual QA, confirmed not to reflect a real product defect (both work correctly once the full event sequence is dispatched), unrelated to this phase's own code, and out of scope to fix here.
- No frontend automated test framework exists in this repository (`06_TECH_STACK.md` §5 still lists it unchosen); this phase did not introduce one, matching Phase 06's precedent.

## Upgrade Notes

None beyond a normal deploy — the migration is additive and runs automatically on backend startup, as every migration since `0001` does.

## Deferred Work

- Pagination — deliberately out of scope; the Hub instead caps results at a fixed 100 with explicit truncation reporting. See `01_SPEC.md` §6.6/§6.7.
- Wiki-style `[[title]]` link parsing — rejected in favor of explicit links. See `01_SPEC.md` §6.5.
- Secrets as Hub content — Secrets remain a credentials surface, not a knowledge surface. See `01_SPEC.md` §5.
- AI/semantic search over knowledge — resolved as "beyond Phase 07," not deferred to a named future phase. See `01_SPEC.md` §5.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
