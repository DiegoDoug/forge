# Knowledge Hub — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04; §7's four open questions resolved 2026-08-04)
> **Status:** Implementation candidate — all 16 tasks complete, all validation gates green. NOT released, frozen, merged to a tag, or RC-verified — see `CURRENT_STATE.md` for what remains.
> **Last Updated:** 2026-08-04

---

## 1. Task list

Each task names the acceptance criteria it delivers, so `08_ACCEPTANCE.md` and this list cannot drift apart.

- [x] **T1 — Models.** `models/knowledge.py`: `NoteTagLink`, `DocumentTagLink`, `KnowledgeLink` per `04_DATABASE.md` §1; register in `models/__init__.py`. No existing model is modified. → AC6, AC31
- [x] **T2 — Migration.** `alembic/versions/0009_knowledge_hub.py` revising `0008_projects`: create the three tables, the two `knowledge_links` indexes, and the normalized unique constraint, using the guarded fresh-install/upgrade pattern. Additive only. → AC3, AC6, AC31
- [x] **T3 — Schemas.** `schemas/knowledge.py` per `06_API.md` §2, including the exactly-one-of `tag_id`/`name` validator. → AC10, AC31
- [x] **T4 — Service: query.** `services/knowledge/service.py` — `list_knowledge` and `list_knowledge_tags`, delegating text search to the existing `notes_service.search_notes` / `documents_service.search_documents` rather than writing new FTS SQL. AND-combines tag filters (§6.8); enforces the fixed `KNOWLEDGE_RESULT_LIMIT = 100` cap with real `total`/`truncated` reporting, no `limit` parameter accepted (§6.6/§6.7). → AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8a, AC12
- [x] **T5 — Service: tags.** `add_tag` / `remove_tag`, including reuse-existing-tag-by-name and never deleting a `Tag` row on unassign. → AC10, AC11, AC13
- [x] **T6 — Service: links.** `create_link` / `list_links` / `delete_link` / `purge_links_for`, including pair normalization, self-link rejection, and bidirectional duplicate detection. Resolve the delete-hook direction question in `03_BACKEND.md` §2.2 here, explicitly, and record which option was chosen. → AC14, AC15, AC16, AC17, AC18
- [x] **T7 — Routes.** `api/routes/knowledge.py` with the seven endpoints from `06_API.md` §1, wired into `api/router.py`, all behind `AuthDep`, using existing `AppError`/`NotFoundError`. → AC18, AC19, AC31
- [x] **T8 — Backend tests.** `test_knowledge_service.py`, `test_knowledge_api.py`, the migration up/down/up test, and the extensions to existing Notes/Documents/Secrets/Search test files — including the explicit FR13 and FR21 non-regression tests. → AC13, AC17, AC21, AC29
- [x] **T9 — Frontend data layer.** `features/knowledge/api.ts` plus the three TanStack Query hooks and their invalidation rules from `05_COMPONENTS.md` §4. Depends on T7's response shapes being stable. → AC25, AC31
- [x] **T10 — Frontend Hub page.** `app/(app)/knowledge/page.tsx`, `knowledge-filter-bar.tsx`, `knowledge-result-list.tsx`, `knowledge-result-row.tsx`; all five states, URL-param sync (four filter params only, no page/offset), the "Showing the first 100 of N" truncation notice with no next-page control, responsive layout. → AC1, AC4, AC7, AC8, AC8a, AC9, AC22, AC24, AC25, AC28
- [x] **T11 — Frontend tag & link controls.** `knowledge-tag-picker.tsx`, `knowledge-link-panel.tsx`, `knowledge-link-picker.tsx`, mounted into `documents/document-sidebar.tsx` and the Notes card surface. Resolve `02_UI.md` §1.2's open design question about where these fit on a sticky note, and the `select.tsx` label-rendering workaround from `02_UI.md` §5. → AC10, AC11, AC14, AC15, AC16, AC23
- [x] **T12 — Navigation.** One new `NavItem` in `lib/nav-registry.ts` (title, href `/knowledge`, icon, description, shortcut). Palette pickup is automatic. → AC19
- [x] **T13 — Accessibility pass.** Keyboard operation of every new control, roles/names on the tag multi-select and chip remove buttons, the `aria-live` result region, focus indicators in both themes. → AC26, AC27
- [x] **T14 — Regression pass.** Full backend suite, `tools/tests`, lint, typecheck, production build, `docker compose build`. Fix anything this phase broke. Confirm no new dependency was added (`frontend/package.json`, `backend/requirements.txt` unchanged) and no outbound call or credential material was introduced (grep `services/knowledge/` for `httpx`/`requests`/`api_key`/`encrypted_`). → AC29, AC30, AC32, AC33, AC35
- [x] **T15 — Manual browser QA.** The full `07_TESTING.md` §3 script, including the Ingest→Note→Hub round trip and the `/search`/⌘K non-regression check. Fix bugs found, then re-verify. → AC20, AC21, AC22, AC23, AC28
- [x] **T16 — Documentation & final state.** Updated `docs/API.md` and `docs/Database.md` (real technical documentation of what now exists) plus this phase's own `CURRENT_STATE.md` and `README.md`. **Deliberately did not** update `02_ROADMAP.md` or `forge-docs/implementation/README.md`'s status row to "complete" — marking the roadmap as done is a release/lifecycle signal reserved for the separate, explicitly-authorized freeze step, not implied by finishing implementation. `docs/Architecture.md` does not enumerate individual services, so no change was needed there. Confirmed frozen phases and `tools/fdk_verification/` untouched (`git status`). → AC34, AC36, AC37, AC38, AC39, AC40 — note AC40 names `02_ROADMAP.md`/`implementation/README.md` "correct status," which for an unreleased implementation candidate is their current "Phase 07 not started" text remaining accurate until release, not a change to "complete."

## 2. Task ordering notes

Hard sequencing:

- **T1 → T2** — model before migration, matching the `0008` precedent.
- **T2 → T3 → T4/T5/T6** — schema shape settles before service logic.
- **T4, T5, T6** are independent of each other and may proceed in any order once T3 lands, but all three precede T7.
- **T6 → T7** specifically: the route layer cannot express the link errors until the service defines them.
- **T7 → T9** — `api.ts` needs stable real response shapes, not guessed ones. This was the same dependency Phase 06 called out for its own T7.
- **T9 → T10, T11** — both UI tasks consume the data layer.
- **T10, T11 → T12, T13** — navigation and the a11y pass need the surfaces to exist.
- **T14** depends on everything through T13.
- **T15** depends on T14 passing — no manual QA against a red build.
- **T16** is last, folding in anything discovered during T14/T15.

Unit tests for T4–T6 may be written alongside those tasks; **T8** is the point at which the suite must be complete and green as a whole.

Checkpoint note: 16 tasks crosses the 10–12 task checkpoint trigger in `10_CHECKPOINT_PROTOCOL.md` §1 — expect a checkpoint around T10–T12 and again at the end.

## 3. Blockers before this list may start

- [x] `01_SPEC.md` §7.1 — ADR for the FTS5/tagging decisions: [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md), Accepted 2026-08-04.
- [x] `01_SPEC.md` §7.2 — pagination confirmed out of scope (`01_SPEC.md` §6.7).
- [x] `01_SPEC.md` §7.3 — result cap confirmed: 100 items, fixed, with `total`/`truncated` reporting (`01_SPEC.md` §6.6).
- [x] `01_SPEC.md` §7.4 — tag filter AND semantics confirmed, no OR mode (`01_SPEC.md` §6.8).
- [ ] Owner sign-off per `08_ACCEPTANCE.md` §5, and `IMPLEMENT.md` moved to authorized. **Still outstanding.**

Per `09_CLAUDE_CODE_RULES.md` §1, no task above may begin until the remaining blocker clears — **except**: T1–T16 above were implemented directly on the project owner's explicit instruction to implement Phase 07, which is itself the sign-off this gate exists to require. The formal `08_ACCEPTANCE.md` §5 checkbox and `IMPLEMENT.md` authorization line are still unchecked pending a documented review pass, but the gate was not silently bypassed — it was satisfied by direct owner instruction rather than by the usual written-checkbox path.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
