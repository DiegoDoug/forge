# Knowledge Hub — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04)
> **Status:** Confirmed — `01_SPEC.md` §7's four open questions resolved 2026-08-04; ready for implementation pending final review
> **Last Updated:** 2026-08-04

---

## 0. What actually exists in this repository

Verified against the repo on 2026-08-04, not assumed:

| Capability | Status | Command |
|---|---|---|
| Backend unit/integration tests | **Exists** — pytest, 255 tests collected | `backend/.venv/Scripts/python.exe -m pytest backend/tests` |
| Frontend lint | **Exists** — ESLint (`frontend/package.json` `lint` script) | `npm --prefix frontend run lint` |
| Frontend typecheck | **Exists** — TypeScript is installed | `frontend/node_modules/.bin/tsc --noEmit` |
| Frontend production build | **Exists** — Next.js | `npm --prefix frontend run build` |
| Full-stack build | **Exists** — Docker Compose | `docker compose build` |
| **Frontend unit/component tests** | **Does not exist** | — |
| **Browser/E2E automation** | **Does not exist** | — |

Every command above was executed during this specification session. Lint and typecheck both exit 0 on the current tree.

There is **no frontend test framework in this repository** — no Vitest, Jest, Testing Library, Playwright, or Cypress in `frontend/package.json`, and zero `*.test.*` / `*.spec.*` files anywhere under `frontend/`. `06_TECH_STACK.md` §5 still lists frontend test tooling as unchosen, and `07_CODING_STANDARDS.md` §4 leaves it TODO.

**Phase 07 does not introduce one.** Adopting a frontend test framework is cross-cutting infrastructure work, not a Knowledge Hub requirement, and adding it here would smuggle an unrelated dependency decision into a feature phase (`09_CLAUDE_CODE_RULES.md` §3 makes new dependencies ask-first). This matches the explicit precedent Phase 06 set in its own `07_TESTING.md` §2.

**Consequence, stated plainly:** frontend correctness in this phase is established by typecheck + lint + a successful production build + the manual QA pass in §3. That is weaker than automated component tests, and it is a known, accepted limitation rather than an oversight.

## 1. Backend tests

New file `backend/tests/test_knowledge_service.py` — unit tests for `services/knowledge/service.py`:

- `list_knowledge` with no filters: returns notes and documents merged, sorted by `updated_at DESC`.
- `list_knowledge` with `q`: delegates to `notes_service.search_notes` / `documents_service.search_documents` — matches in either type appear; a term matching neither returns empty. Assert (via mock/spy) that `list_knowledge` calls these existing functions rather than issuing its own `MATCH` SQL, so a future regression toward a parallel FTS implementation fails loudly (§0's ADR-0015 compliance).
- `list_knowledge` with `type=note` / `type=document`: excludes the other type entirely.
- **`list_knowledge` tag filter — AND semantics, the only mode (`01_SPEC.md` §6.8).** With one tag: returns exactly the items carrying it. With two tags: returns only items carrying **both** — construct a fixture where item A has tag X only, item B has tag Y only, and item C has both X and Y; filtering by `[X, Y]` must return only C, never A or B. There is no code path or parameter that produces OR behavior — no test exercises one, because none exists.
- `list_knowledge` with `project_id`: only items scoped to that project; unscoped items excluded.
- Filters combined: query + type + tag + project simultaneously.
- **Result cap, exactly 100 (`01_SPEC.md` §6.6).** Seed 105 matching items: `list_knowledge` returns exactly 100 items, `total == 105`, `truncated is True`. Seed exactly 100: returns 100 items, `truncated is False`. Seed 99: returns 99, `truncated is False`. The returned 100 are the **most recently updated** — assert the 5 oldest of the 105 are absent, not an arbitrary 5.
- **No pagination path exists.** `list_knowledge`'s signature has no `offset`/`page`/`cursor` parameter — assert via `inspect.signature` that only `session, q, item_type, tag_ids, project_id` (or equivalent) are accepted, so a future PR cannot silently reintroduce pagination without this test failing.
- `list_knowledge_tags`: returns only tags assigned to notes/documents, with correct counts; a tag used **only** by a Secret does not appear.
- `add_tag` by existing id; by new name (creates); by existing name (reuses, does not duplicate or raise).
- `remove_tag`: unassigns, and the `Tag` row still exists afterwards.
- `create_link`: note→note, note→document, document→document all succeed.
- `create_link` self-link → rejected; duplicate in the same direction → rejected; duplicate in the **reverse** direction → rejected (the normalization case).
- `list_links` returns the link from both endpoints, with `other` correctly oriented from each side.
- `delete_link`: removes the row; both items survive.
- `purge_links_for`: deleting a note/document removes every link referencing it from **either** side, leaving no orphans (`01_SPEC.md` FR17 — the service-enforced integrity from `04_DATABASE.md` §2).

New file `backend/tests/test_knowledge_api.py` — integration tests for `api/routes/knowledge.py`:

- Auth required on every one of the seven routes (unauthenticated → 401).
- `GET /api/knowledge` end-to-end with each of the four query parameters (`q`, `type`, `tag_id` repeated, `project_id`) and with all of them combined.
- **`GET /api/knowledge` accepts no `page`/`offset`/`cursor`/`limit` parameter.** Assert the endpoint ignores or 422s an unexpected extra query parameter per FastAPI's normal behavior — there is nothing named `limit` for a caller to pass in the first place, so this is really an assertion that the documented four-parameter contract in `06_API.md` §1.1 is the whole contract.
- `GET /api/knowledge` with 105 seeded matching items: response has exactly 100 `items`, `total: 105`, `truncated: true`. With ≤100 seeded items: `truncated: false` and `total == len(items)`.
- `GET /api/knowledge` with two `tag_id` values: only items carrying both are returned (AND) — the API-level equivalent of the service-level AND test above, over real HTTP.
- Unknown `item_type` → 422; unknown item id → 404; unknown link target → 404.
- Self-link → 400 `knowledge_link_self`; duplicate link → 409 `knowledge_link_duplicate`.
- Tag assign with both `tag_id` and `name` → 422; with neither → 422.
- Full round trip: create tag → assign → appears in `GET /api/knowledge` item tags and in `GET /api/knowledge/tags` counts → unassign → gone from both.
- Full round trip: create link → visible from both endpoints → delete → gone from both.

Extensions to **existing** test files (extend, never replace):

- `test_notes*` / `test_documents*` — add coverage that deleting an item purges its knowledge links, and that all pre-existing behavior is unchanged.
- A Secrets-side test asserting that assigning knowledge tags leaves `secret_tag_links` and every Secrets endpoint untouched (`01_SPEC.md` FR13).
- A test asserting `GET /api/search`'s response shape and behavior are **byte-for-byte unchanged** by this phase (`01_SPEC.md` FR21).

Migration test: `0009_knowledge_hub` exercised `upgrade → downgrade → upgrade` against a throwaway SQLite file, asserting pre-existing seeded `notes` / `documents` / `secrets` / `tags` / `secret_tag_links` rows survive untouched — the same pattern Phase 06 used for `0008`.

## 2. Build / lint / type checks

Run from the repository root:

```
npm --prefix frontend run lint
frontend/node_modules/.bin/tsc --noEmit
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/tests
docker compose build
```

All five must pass with zero errors before the phase reaches Release Candidate. `tsc --noEmit` is listed separately from `next build` deliberately: it is faster to run during development, and it is the check that catches the `api.ts` type drift most likely to appear in this phase.

## 3. Manual QA

Executed against a real browser preview with throwaway data. This is the **only** verification path for UI behavior in this phase (§0).

- Hub with zero notes and zero documents → the "no knowledge at all" empty state, with working links to Notes and Documents.
- Create several notes and documents → all appear in the Hub with correct type badges, titles, excerpts, and timestamps.
- Text query matching a note only, a document only, and both → correct results each time; a nonsense term → the "no matches" empty state (distinct from the previous one).
- Type filter → Notes only, then Documents only, then All.
- Assign tags from the Document sidebar and from a Note; verify the chips appear in the Hub list.
- Inline-create a brand-new tag; then assign an existing tag by typing its exact name → reuses, does not duplicate.
- Tag filter with one tag, then two → the two-tag case narrows to items carrying **both** (AND, `01_SPEC.md` §6.8), not the union; the tag list shows accurate counts.
- Project filter, using a project from Phase 06 → only that project's items.
- All filters at once; then "Clear filters."
- Filters reflected in the URL → refresh the page → the filtered view is restored.
- Seed more than 100 matching items and exceed the result cap → the explicit "Showing the first 100 of N — narrow your filters" notice appears (`02_UI.md` §1.1), not a silent cut. Confirm no "load more," "next page," or page-number control exists anywhere on the Hub — this phase has no pagination.
- Click a note result → lands on Notes. Click a document result → lands on that document.
- Link a note to a document → open the document → the note appears in its linked items, and vice versa.
- Attempt to link an item to itself, and to create a duplicate link → both show inline validation errors, not a crash or a vanished toast.
- Delete a linked note → the link disappears from the other item; the other item survives intact.
- Confirm a tag assigned to a knowledge item does **not** appear on any Secret, and Secrets' own tag UI is unchanged.
- Confirm `/search` and ⌘K behave exactly as before, including Secrets results.
- Keyboard-only pass: every filter control, the tag picker, the link picker, and result-row activation.
- Screen-reader pass on the result count / truncation live region and the tag chip remove buttons.
- Light and dark theme; desktop and mobile viewport widths (`02_UI.md` §4).

> Per the Phase 06 checkpoint's recorded risk, if the Browser pane cannot composite a screenshot, verify visual claims via computed-style / `getBoundingClientRect()` inspection and **say so explicitly** in the checkpoint rather than implying a screenshot pass.

## 4. Accessibility verification

No automated a11y tooling exists in this repo. Verification is manual, against `02_UI.md` §5:

- Keyboard-only operation of every new control.
- Accessibility-tree inspection confirming roles/names on the tag multi-select, result rows, and tag chip remove buttons.
- `aria-live` region announces result-count changes.
- Visible focus indicators throughout, in both themes.

Anything that cannot be verified this way becomes a QA ticket per `12_BUG_CLASSIFICATION.md` §4, not a silent pass.

## 5. Regression risk

- **Notes** — board, cards, drag/positioning, pin/archive, FTS search, existing endpoints. Verified by the existing Notes tests passing unmodified, plus manual board QA.
- **Documents** — editor, history sidebar, and the txt/md/xml/doc/docx/pdf export pipeline. Export is untouched by this phase; verified by existing Documents tests passing unmodified and one manual export.
- **Secrets** — tags are the shared surface and the highest-risk neighbor. Existing Secrets tests must pass unmodified, plus the explicit FR13 test in §1.
- **Search / command palette** — must be bit-identical in behavior (FR21). Existing search tests unmodified, plus the explicit response-shape test.
- **Projects (Phase 06)** — the Hub reads `project_id` but never writes it. Existing Projects tests unmodified.
- **Ingest** — untouched; its `to-note` path must still work end to end (manual QA: ingest a file, save as note, find it in the Hub).
- **Migration chain** — `0009` must apply cleanly after `0008` on both a fresh install and an existing populated database.
- **FDK verification tooling** — `backend/.venv/Scripts/python.exe -m pytest tools/tests` must remain green; this phase must not touch `tools/fdk_verification/`.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [01_SPEC.md](01_SPEC.md)
- [../../06_TECH_STACK.md](../../06_TECH_STACK.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
