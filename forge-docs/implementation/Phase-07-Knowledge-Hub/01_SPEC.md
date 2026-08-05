# Knowledge Hub — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04; §7's four open questions resolved 2026-08-04)
> **Status:** Confirmed — ready for `IMPLEMENT.md` authorization pending final review
> **Last Updated:** 2026-08-04

---

## 1. Summary

Introduce the **Knowledge Hub**: one place to browse, search, tag, and link everything Forge treats as knowledge — Notes and Documents, including the Markdown that Ingest produces once it is saved as a Note.

The Hub is an **organizational and retrieval layer over existing content**, not a replacement for the features that own it. Notes stay on the Notes board; Documents stay in the Documents editor; Ingest stays a transient conversion pipeline. What Phase 07 adds is a single surface that sees across them, plus the two capabilities the objective names and Forge does not yet have for this content: **consistent tagging** and **linking**.

"Consolidates" here means *unifies access to*, not *rewrites*. No existing note, document, or ingest behavior changes.

## 2. User stories

- As a user whose knowledge is split across sticky notes and long-form documents, I want one page that lists all of it, so I can find something without first remembering which feature I put it in.
- As a user searching for a phrase, I want to search notes and documents together and see which type each result is, so I get one answer list instead of two half-answers.
- As a user with lots of content, I want to tag notes and documents with the same tag vocabulary I already use for Secrets, so "client-a" means the same thing everywhere.
- As a user narrowing down, I want to filter the Hub by tag, by type, and by project, so I can get from "everything" to "the four things I care about" in a couple of clicks.
- As a user who knows two pieces of content are related, I want to explicitly link them, so that opening either one shows me the other.
- As a user who ingested a PDF into a Note, I want that Note to be findable and taggable in the Hub like anything else, without ingest growing its own storage.
- As a user who already relies on ⌘K and `/search`, I want those to keep working exactly as they do today.

## 3. Functional requirements

### Hub view

- **FR1.** A dedicated Knowledge Hub page at `/knowledge` lists knowledge items — Notes and Documents — in one unified, type-labelled list. Each entry shows: type, title (or "Untitled"), a content excerpt, its tags, its project (if any), and last-updated time.
- **FR2.** The Hub accepts a full-text query that searches notes and documents together, using the **existing** `notes_fts` / `documents_fts` FTS5 indexes. No new index is introduced (see §6.4, ratified by [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md)).
- **FR3.** The Hub can filter by item type: all / notes only / documents only.
- **FR4.** The Hub can filter by one or more tags, using **AND** semantics: an item must carry **every** selected tag to match. Selecting tags A and B returns only items tagged with both A and B — an item carrying just one of the two is excluded. This is a final decision, not a default subject to change; there is no OR mode (see §6.6).
- **FR5.** The Hub can filter by project, reusing the `project_id` that Notes and Documents already carry from Phase 06. No new scoping concept is introduced.
- **FR6.** Filters compose — a query, a type, tags, and a project can all be active at once — and results default to most-recently-updated first.
- **FR7.** Selecting a result navigates to that item where it already lives (the Notes board for a Note, the Document editor for a Document). The Hub does **not** embed or duplicate either editor.
- **FR8.** The Hub defines explicit empty, loading, error, and populated states, including the distinct "no items at all" and "no items match these filters" empty states.
- **FR8a.** The Hub returns **no more than 100 matching items** in a single response, ordered by `updated_at` descending before truncation is applied, so the cap always drops the least-recently-updated tail rather than an arbitrary slice. The Hub has **no pagination** — there is no page/offset/cursor parameter, and none is planned for this phase (see §6.7). When the true match count exceeds 100, the response reports the real total and a truncation flag, and the UI shows an explicit "showing the first 100 of N — narrow your filters" notice. A truncated result is never presented as if it were complete.

### Tagging

- **FR9.** A Note or a Document can be assigned zero or more tags, drawn from the **existing shared `tags` table** — the same vocabulary Secrets already uses.
- **FR10.** A user can create a new tag inline while tagging an item. Tag names remain globally unique (existing constraint); assigning an existing name reuses that tag rather than creating a duplicate.
- **FR11.** A user can remove a tag from a Note or Document. Removing an assignment never deletes the tag itself, because the tag may be in use elsewhere — including by Secrets.
- **FR12.** The Hub's tag filter lists the tags actually in use by knowledge items, each with the count of matching items, so a user is never offered a filter that returns nothing.
- **FR13.** Tagging a Note or Document has **no effect** on any Secret's tag assignments, and no Secrets endpoint or behavior changes. The `tags` table is shared vocabulary only; the link tables are separate (see §6.3).

### Linking

- **FR14.** A user can create an explicit link between two knowledge items in any combination: note↔note, note↔document, document↔document.
- **FR15.** A link is **visible from both sides**. Opening either item shows the other in its linked-items list. The stored row has a source and a target, but the product behavior is undirected — there is no "backlink" concept distinct from a link.
- **FR16.** A user can remove a link from either side. Removing a link never deletes either item.
- **FR17.** Deleting a Note or a Document removes every link that referenced it. No orphaned link may remain (see §6.5 for why this is service-enforced rather than a foreign key).
- **FR18.** An item cannot be linked to itself, and the same pair cannot be linked twice regardless of which side initiated it. Both are rejected with a clear validation error, not silently ignored.

### Integration

- **FR19.** The Knowledge Hub is reachable from the sidebar and the command palette, per `04_UI_GUIDELINES.md` §2.
- **FR20.** Ingest output reaches the Hub through the **already-shipped** "save converted file as Note" path (`POST /api/ingest/jobs/{job_id}/files/{task_id}/to-note`). Once saved, it is a Note and is searchable, taggable, and linkable like any other Note. Ingest gains no database table, no persistence change, and no new endpoint.
- **FR21.** `/search`, `GET /api/search`, and the ⌘K command palette are **unchanged** by this phase — same route, same response shape, same behavior, including their existing coverage of Secrets. This is a hard compliance requirement of ADR-0007 (see §6.2).

## 4. Relationship to existing features

| Feature | Relationship | What changes |
|---|---|---|
| **Notes** | Reused and extended | Gains tag assignments and link participation. Note model, board UI, FTS index, and all existing endpoints are unchanged. |
| **Documents** | Reused and extended | Same as Notes. The rich-text editor, history sidebar, and the txt/md/xml/doc/docx/pdf export pipeline (`services/documents/export.py`) are **not touched** — see §5. |
| **Ingest** | Linked/integrated only | No change at all. Its existing `to-note` handoff is the integration point (FR20). Jobs stay in-memory with TTL-expiring disk artifacts, exactly as `services/ingest/jobs.py` documents. |
| **Search** | Neither reused nor changed | The Hub is a separate surface with its own endpoint. `GET /api/search` keeps its own aggregation and its own Secrets coverage. See §6.2. |
| **Projects (Phase 06)** | Reused as-is | The Hub reads the existing nullable `project_id` on Notes and Documents. No new column, no change to project semantics. |
| **Secrets** | Out of the Hub's content model | Secrets are credentials, not knowledge. They keep their own tags, their own page, and their existing presence in `/search`. See §5. |

## 5. Explicitly out of scope

- **Secrets as Hub content.** The objective names Notes, Documents, and Ingest output. Putting encrypted credentials into a browse-everything knowledge surface is a security-posture change (`docs/Security.md`), not an organizational one. Secrets remain searchable via `/search` exactly as today.
- **Wiki-style `[[title]]` links parsed from content.** Considered and rejected for this phase — see §6.5.
- **A new search index, a `knowledge` table, or merging Notes and Documents into one model.** The Hub is a query layer over two existing FTS5 indexes — see §6.4.
- **Pagination.** `02_ROADMAP.md` §5 names Phase 07 as a *candidate* for folding in Forge-wide pagination — a candidate, not a requirement. **This phase does not introduce pagination.** No page, offset, or cursor parameter exists on `GET /api/knowledge` or any other Phase 07 endpoint, and the Hub UI has no "next page" control. Phase 07 follows the exact convention Phase 06 already set (unpaginated lists, capped result sets), and leaves Forge-wide pagination to a dedicated future effort. The bounded-result need this creates is met by the 100-item cap in FR8a, not by pagination — see §6.7. This decision is final, not a placeholder pending §7.
- **Editing note or document content inside the Hub.** The Hub navigates to the owning editor (FR7). Building a third editing surface would duplicate two shipped ones.
- **Changing the Documents export pipeline.** Phase 04's spec calls this "Phase 07 territory," but that was Phase 04 disclaiming scope, not Phase 07 committing to it. Nothing in the Knowledge Hub objective requires export changes.
- **Refactoring `secret_tag_links` into a polymorphic tag table.** Rejected — see §6.3.
- **Persisting Ingest artifacts.** Deliberately excluded; ingest's transient design is intentional per its own module docstring.
- **AI-assisted features over knowledge** (semantic search, embeddings, summarization, inline AI editing). Phase 06 deferred "deep AI-assisted editing inside Notes/Documents" to "Knowledge Hub or beyond" — this phase resolves that as **beyond**. Phase 07 adds no outbound network calls and no provider dependency.

## 6. Decisions

These were confirmed by the project owner on 2026-08-04. Each records the alternatives that were rejected, because the rejected options are the ones a later session is most likely to re-propose.

### 6.1 The Hub is a distinct surface, not a rewrite

**Decision:** Knowledge Hub is an aggregation/organization layer. Notes, Documents, and Ingest keep their models, their pages, and their behavior.

**Why:** "Consolidates" in `02_ROADMAP.md` is a one-word summary, not a mandate to merge data models. Merging Notes and Documents would rewrite two shipped, frozen-phase features to deliver an organizational capability that does not require it — maximum risk for zero user-visible gain.

### 6.2 New `/knowledge` page — `/search` is left alone

**Decision:** A new route `/knowledge` with its own endpoint (`GET /api/knowledge`). `/search`, `GET /api/search`, and the ⌘K palette are untouched.

**Rejected — evolve `/search` into the Hub:** would supersede [ADR-0007](../../decisions/0007-search-dedicated-page.md), whose §6 explicitly states its accepted scope "remains exactly §2: a `/search` results page reusing the existing `GET /api/search` endpoint" and directs that it not be expanded "without a new decision." It would also drag Secrets into a knowledge-browsing view, contradicting §5.

**Rejected — build the Hub *and* extend `GET /api/search` with tag/type filters:** larger blast radius. `GET /api/search` is a shared contract consumed by both `/search` and the command palette; changing it puts two shipped surfaces at regression risk to benefit one new one.

**Compliance note:** ADR-0007 is not modified or superseded by this phase. Phase 07 complies with it by leaving its subject matter alone entirely. The two surfaces answer different questions — `/search` is "find this thing now," the Hub is "browse and organize what I know" — so `01_PRODUCT_PRINCIPLES.md` §1.7 ("one search") is not violated: there is still exactly one *search* implementation per index, and the Hub queries the same FTS5 indexes rather than growing a second one.

### 6.3 Knowledge-scoped tag link tables, shared tag vocabulary

**Decision:** Add `note_tag_links` and `document_tag_links`, both referencing the **existing** `tags` table — mirroring the proven `secret_tag_links` pattern. Additive migration only.

**Why:** one shared vocabulary is what "consistent tagging" means in the objective, and the pattern already exists and works. Nothing shipped is modified.

**Rejected — a separate `knowledge_tags` taxonomy:** would force the user to maintain two vocabularies where "client-a" as a Secret tag and "client-a" as a Note tag are different rows. That is the opposite of "consistent tagging."

**Rejected — generalize to one polymorphic `taggables` table:** cleanest long-term shape, but it requires migrating shipped `secret_tag_links` data and altering a frozen phase's schema. The risk is real and the benefit is deferred; the cost of adding a third link table later, if a third taggable type ever appears, is low. Revisit then.

### 6.4 Extend the existing FTS5 setup; no new index

**Decision:** The Hub queries the existing `notes_fts` and `documents_fts` external-content FTS5 indexes (kept in sync by triggers from the initial migration). No new index, no new content table.

**Why:** this resolves the open architectural question recorded at `03_ARCHITECTURE.md` §4 — *"Does Knowledge Hub introduce a new search index, or extend the existing FTS5 setup used by Notes?"* — in favor of extending. Both indexes already exist, are trigger-maintained, and already back `notes_service.search_notes` and `documents_service.search_documents`. A third index would need its own sync triggers and could drift from the two sources of truth.

> **Ratified.** [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md) — accepted 2026-08-04 — closes `03_ARCHITECTURE.md` §4's open question in favor of this decision (and ratifies §6.3's tag-table shape alongside it). `03_ARCHITECTURE.md` §4 now points back to it.

### 6.6 Result cap: 100 items, no pagination

**Decision:** `GET /api/knowledge` returns at most 100 items per request, ordered by `updated_at` descending before the cap is applied. There is no pagination — no page, offset, or cursor parameter, on this or any other Phase 07 endpoint. When the true match count exceeds 100, the response carries the real `total` and a `truncated: true` flag (see `06_API.md` §1.1), and the UI renders an explicit notice rather than a silent cut (FR8a).

**Why:** Phase 07 follows Phase 06's precedent exactly — unpaginated lists, capped result sets — rather than solving Forge-wide pagination as a side effect of one feature phase. `02_ROADMAP.md` §5 lists pagination as a candidate to fold into whichever phase touches it, not a requirement Phase 07 must satisfy. 100 was chosen as a round, generous number well above the existing precedents in this codebase (`global_search` caps at 10 per type; the FTS5 helpers themselves cap at 50) — large enough that hitting the cap should be rare for a real user's knowledge base, while still bounding response size and render cost.

**Rejected — build pagination now:** would make Phase 07 responsible for solving a tracked, Forge-wide gap as an unplanned side effect, expanding scope well beyond "browse, tag, and link." No user story in §2 asks for it.

**Rejected — an unbounded result set:** with no cap, a large knowledge base returns every match in one response — unbounded response size and render cost, and no way to communicate "there's more than this" to the user. Per `01_PRODUCT_PRINCIPLES.md` §1.3 (honest gaps over fake completeness), an unindicated silent cut would be worse than an explicit one, so a cap with a truncation notice was chosen over both extremes.

**Rejected — a smaller cap (e.g. 20, matching a typical single-screen list):** would make truncation the common case rather than the rare one, degrading the Hub for any moderately active user. 100 was chosen precisely so truncation is exceptional.

### 6.7 Pagination is out of scope for this phase

**Decision:** no pagination exists anywhere in Phase 07. This is a final scope decision, not a placeholder awaiting a later choice — see §6.6, which is the mechanism that makes this possible without an unbounded response.

**Why:** stated fully in §6.6 and in §5's "Pagination" bullet. Recorded as its own decision so it cannot be read as still-open.

### 6.8 Tag filter semantics: AND

**Decision:** selecting multiple tags in the Hub's filter returns only items carrying **every** selected tag — AND, not OR (FR4).

**Why:** matches how a user reads a multi-select tag filter ("show me things tagged both X and Y"), and matches the more restrictive, more predictable of the two options. A user who wants either-or coverage can run the filter twice or omit one tag; a user who wants strict narrowing has no way to get AND if OR is the only mode.

**Rejected — OR semantics:** plausible, but was not chosen. It is not offered as a hidden or future mode — the API and UI implement AND only, per `06_API.md` §1.1 and `08_ACCEPTANCE.md` AC5.

### 6.5 Explicit related-item links, not content-parsed wiki links

**Decision:** A user explicitly links two items. One `knowledge_links` table; links are visible from both sides (FR15).

**Why:** objectively testable, no content parsing, no rendering changes to either editor, and it satisfies the objective's "linking" without inventing a syntax.

**Rejected — wiki-style `[[title]]` links parsed from content:** requires a content parser, a title-resolution and ambiguity model (titles are not unique — `Note.title` and `Document.title` are both non-unique and default to `""`), and changes to both the Markdown renderer and the rich-text editor. That is a phase's worth of work on its own, and it would couple the Hub to both editors' internals — the exact cross-feature coupling `03_ARCHITECTURE.md` §2 forbids.

**Rejected — defer linking entirely:** the objective names linking explicitly. Dropping it would leave the phase failing its own stated goal.

**Consequence:** because a link can span two tables, `knowledge_links` stores `(item_type, item_id)` pairs rather than two foreign keys. SQLite cannot enforce referential integrity across a polymorphic reference, so FR17 (no orphaned links) is enforced in the service layer on delete, and is an explicit acceptance criterion and test case rather than a database guarantee. This is the one place this phase accepts a weaker integrity guarantee than the rest of the schema; `04_DATABASE.md` §2 records it.

## 7. Open questions

**None blocking.** The four questions this section originally raised were all resolved by the project owner on 2026-08-04:

| # | Question | Resolution |
|---|---|---|
| 7.1 | ADR for the FTS5/tagging decision | [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md), Accepted 2026-08-04 — see §6.4 |
| 7.2 | Pagination in or out of scope | Out of scope, final — see §5, §6.7 |
| 7.3 | Result cap value | 100 items, with explicit truncation reporting — see §6.6 |
| 7.4 | Tag filter AND vs. OR | AND, final, no OR mode — see §6.8 |

This document, `08_ACCEPTANCE.md`, `06_API.md`, and `09_IMPLEMENTATION_TASKS.md` have all been updated to reflect these resolutions consistently. Nothing in this specification remains contingent on a decision not yet made.

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../decisions/0007-search-dedicated-page.md](../../decisions/0007-search-dedicated-page.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
- [../../decisions/0015-knowledge-hub-reuses-fts5.md](../../decisions/0015-knowledge-hub-reuses-fts5.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
