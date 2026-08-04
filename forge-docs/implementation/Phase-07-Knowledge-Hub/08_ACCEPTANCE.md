# Knowledge Hub — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04)
> **Status:** All 41 criteria verified against the implementation (backend tests, manual browser QA against a real running instance) — see `CURRENT_STATE.md` for what still gates release (owner sign-off, §5 below).
> **Last Updated:** 2026-08-04

---

> Every criterion below names what is checked and how it is observed, so it can be judged true or false without interpretation. 41 criteria total: AC1–AC40 plus AC8a, added alongside AC8 to state the result-cap/no-pagination behavior (`01_SPEC.md` §6.6/§6.7) without renumbering everything after it. All checked below were verified directly — automated test names are cited per-criterion; where QA was manual (UX/visual/keyboard criteria), it was performed against a real running instance in this session, not assumed.

## 1. Functional acceptance criteria

Traces to `01_SPEC.md` §3.

- [x] **AC1 (FR1).** `/knowledge` lists both Notes and Documents in one list. With N notes and M documents present, the Hub shows N+M items, each carrying a type badge that matches its source, a title (or "Untitled"), an excerpt, its tags, its project, and a last-updated time.
- [x] **AC2 (FR2).** A query matching only a note's content returns that note; a query matching only a document's content returns that document; a query matching both returns both. A query matching neither returns zero items and the filtered-empty state.
- [x] **AC3 (FR2, §6.4).** No new FTS index or content table exists. Verified by inspecting migration `0009_knowledge_hub.py` for any `fts` DDL (there must be none) and by confirming `services/knowledge/service.py` calls `notes_service.search_notes` / `documents_service.search_documents` rather than issuing its own `MATCH` SQL.
- [x] **AC4 (FR3).** `type=note` returns only notes; `type=document` returns only documents; `type=all` returns both.
- [x] **AC5 (FR4, §6.8).** Filtering by one tag returns exactly the items carrying it. Filtering by two tags returns only items carrying **both** (AND) — a fixture item carrying just one of the two selected tags is excluded. No request or UI control produces OR results; this is the only mode.
- [x] **AC6 (FR5).** Filtering by a project returns only items whose `project_id` matches; unscoped items are excluded. No new scoping column was added (verified against `04_DATABASE.md` §1 — three new tables, no `ALTER TABLE`).
- [x] **AC7 (FR6).** A query, a type, a tag set, and a project applied simultaneously return the intersection. With no query, results are ordered by `updated_at` descending.
- [x] **AC8 (FR7).** Activating a note result navigates to `/notes`; activating a document result navigates to `/documents`. The Hub renders no note or document editor of its own. Per `02_UI.md` §1.1, per-item deep linking is best-effort only — neither feature has a per-item route today, and adding one is out of scope; landing on the correct page is what this criterion requires.
- [x] **AC8a (FR8a, §6.6/§6.7).** `GET /api/knowledge` returns at most 100 items, ordered by `updated_at` descending before the cap is applied. With 105 matching items, the response contains exactly 100 items, `total: 105`, `truncated: true`, and the 100 returned are the most recently updated (the 5 oldest matches are excluded, not an arbitrary 5). `GET /api/knowledge` accepts no `page`, `offset`, `cursor`, or `limit` parameter — the cap is a fixed server constant, not caller-configurable, and no other Phase 07 endpoint accepts one either.
- [x] **AC9 (FR8).** Four distinct states are observable: loading skeleton; "no knowledge at all" empty state; "no items match these filters" empty state with a clear-filters action; populated list. The two empty states are visibly different.
- [x] **AC10 (FR9–FR10).** A tag can be assigned to a Note and to a Document from their own editing surfaces. Assigning a brand-new name creates one `tags` row; assigning an existing name reuses that row — after both operations the `tags` table contains exactly one row for that name.
- [x] **AC11 (FR11).** Removing a tag from an item removes only the assignment; the `Tag` row still exists and remains assigned to any other item that had it.
- [x] **AC12 (FR12).** `GET /api/knowledge/tags` returns only tags assigned to at least one Note or Document, each with a count equal to the number of matching items. A tag assigned only to a Secret does not appear.
- [x] **AC13 (FR13).** After assigning knowledge tags, every Secrets endpoint returns identical responses to before, and `secret_tag_links` is unchanged. Verified by the existing Secrets test suite passing unmodified plus the explicit FR13 test.
- [x] **AC14 (FR14).** Links can be created note→note, note→document, and document→document. All three combinations persist and are retrievable.
- [x] **AC15 (FR15).** A link created from item A to item B appears in **both** A's and B's linked-items lists, with the `other` field correctly identifying the opposite item from each side.
- [x] **AC16 (FR16).** Deleting a link from either side removes it from both sides. Both items still exist and are unchanged.
- [x] **AC17 (FR17).** Deleting a Note or Document removes every `knowledge_links` row referencing it from either the source or target side. A direct database query for links referencing the deleted id returns zero rows.
- [x] **AC18 (FR18).** Linking an item to itself returns `400 knowledge_link_self`. Creating a link that already exists — in either direction — returns `409 knowledge_link_duplicate`. Neither is silently ignored.
- [x] **AC19 (FR19).** Knowledge Hub appears in the sidebar and is reachable from the ⌘K command palette.
- [x] **AC20 (FR20).** Converting a file via Ingest and saving it as a Note produces an item that appears in the Hub, is taggable, and is linkable. Ingest gained no database table and no new endpoint.
- [x] **AC21 (FR21).** `GET /api/search` returns the same response shape and content as before this phase, `/search` behaves identically, and the ⌘K palette still returns Secrets results. Verified by the explicit response-shape test plus the existing search tests passing unmodified. ADR-0007 is unmodified.

## 2. UX acceptance criteria

Derived from `02_UI.md`.

- [x] **AC22.** Every screen state in `02_UI.md` §3 is present and reachable: Hub loading, both empty states, error-with-retry, populated; tag control loading/empty/populated; linked-items empty/populated.
- [x] **AC23.** Self-link and duplicate-link errors render **inline** next to the control, not as a transient toast that disappears before it can be read.
- [x] **AC24.** Whenever the API returns `truncated: true`, the Hub shows "Showing the first 100 of N — narrow your filters" (N is the real `total`). When `truncated: false`, no truncation notice appears at all. No result set is silently cut, and no "load more" / "next page" / page-number control exists anywhere on the Hub — this phase has no pagination.
- [x] **AC25.** Active filters (`q`, `type`, `tag_id`, `project_id`) are encoded in the URL; reloading a filtered Hub URL restores exactly that filtered view. No page/offset parameter is ever part of the URL, because none exists.
- [x] **AC26.** Every new interactive element — query input, type selector, tag multi-select, project selector, result rows, tag chips and their remove buttons, link picker, link remove — is reachable and operable by keyboard alone, with a visible focus indicator.
- [x] **AC27.** The result count / truncation notice is inside an `aria-live="polite"` region and announces when filtering changes the result set. Tag chip remove buttons have accessible names of the form "Remove tag <name>".
- [x] **AC28.** All new surfaces render correctly in light and dark theme and remain usable at mobile viewport widths, with the result list stacking rather than scrolling horizontally.

## 3. Quality acceptance criteria

- [x] **AC29.** All tests in `07_TESTING.md` pass — the full backend suite (`backend/.venv/Scripts/python.exe -m pytest backend/tests`) with the new `test_knowledge_service.py` and `test_knowledge_api.py`, and the migration up/down/up test.
- [x] **AC30.** `npm --prefix frontend run lint`, `frontend/node_modules/.bin/tsc --noEmit`, `npm --prefix frontend run build`, and `docker compose build` all exit 0.
- [x] **AC31.** No architectural invariant in `03_ARCHITECTURE.md` §2 is violated: routers stay thin, no cross-feature import between `notes` and `documents` was introduced, models remain the schema source of truth, and the schema change ships as explicit migration `0009_knowledge_hub.py`.
- [x] **AC32.** No new external dependency was added — `frontend/package.json` and `backend/requirements.txt` are unchanged, and `06_TECH_STACK.md` needs no new entry.
- [x] **AC33.** The phase adds zero outbound network calls and stores no credential material. Verified by code review of `services/knowledge/` and a grep for `httpx` / `requests` / `api_key` / `encrypted_` in the new module returning nothing.
- [x] **AC34.** `08_DEFINITION_OF_DONE.md`'s feature-level checklist is satisfied.
- [x] **AC35.** The FDK verification tooling is untouched and still green: `backend/.venv/Scripts/python.exe -m pytest tools/tests` passes, and `git diff` shows no change under `tools/fdk_verification/` or `tools/tests/`.
- [x] **AC36.** Frozen phases are unmodified: `git diff` shows no change under `forge-docs/implementation/Phase-05-Model-Playground/` or `Phase-06-Projects/`, and no change to `forge-docs/decisions/0007-search-dedicated-page.md`.

## 4. Documentation acceptance criteria

- [x] **AC37.** `docs/API.md` documents all seven new endpoints from `06_API.md` §1.
- [x] **AC38.** `docs/Database.md` documents the three new tables, including the polymorphic-link integrity trade-off from `04_DATABASE.md` §2.
- [x] **AC39.** `CURRENT_STATE.md` reflects reality with no stale "In Progress" items, and `README.md`'s Definition of Complete is satisfied.
- [x] **AC40.** `02_ROADMAP.md` and `forge-docs/implementation/README.md` show Phase 07's correct status.

## 5. Sign-off

- [x] Project owner signs off that the Hub matches the intended scope in `01_SPEC.md`, and that `01_SPEC.md` §7's open questions were resolved before implementation began. **Recorded 2026-08-05**, following the third Release Candidate run (PASS, `forge-docs/history/2026-08-05-phase-07-verification-report.md`) and the repository-state cleanup that preceded it (`be5b227`, `36d2ffa`). This checkbox records sign-off only — it does not itself release, tag, freeze, merge, or advance the phase; those remain separate, not-yet-authorized steps per `13_PHASE_LIFECYCLE.md`.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
