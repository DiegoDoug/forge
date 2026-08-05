# ADR-0015 — Knowledge Hub reuses the existing FTS5 indexes; Search stays untouched

> **Purpose:** Resolve whether Knowledge Hub (Phase 07) introduces a new search index or extends the existing FTS5 setup — closing the open question tracked in [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md) §4. Also ratifies the knowledge-scoped tag link table shape from the same specification session.
> **Scope:** Knowledge Hub's search/query architecture and tag-link table shape. Not the full Phase 07 feature spec — that's [`../implementation/Phase-07-Knowledge-Hub/01_SPEC.md`](../implementation/Phase-07-Knowledge-Hub/01_SPEC.md).
> **Ownership:** Project owner (approved 2026-08-04)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-08-04
> **Depends On:** [ADR-0007](0007-search-dedicated-page.md), [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md), [../implementation/Phase-07-Knowledge-Hub/01_SPEC.md](../implementation/Phase-07-Knowledge-Hub/01_SPEC.md)
> **Supersedes:** —

---

## 1. Context

`03_ARCHITECTURE.md` §4 has carried an open question since Phase 01: *"Does Knowledge Hub introduce a new search index, or extend the existing FTS5 setup used by Notes?"* Phase 07's specification session (2026-08-04) reached an answer, but a root FDK document's open question is not a phase spec's to close unilaterally — per [`09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) §3, "any decision that would need an entry in `decisions/README.md`" is an ask-first action, and this is exactly that: a choice that changes an architectural invariant's open item in `03_ARCHITECTURE.md` §2/§4.

Two existing, independent FTS5 setups already exist and are proven in production: `notes_fts` (backing `notes_service.search_notes()`) and `documents_fts` (backing `documents_service.search_documents()`), both external-content indexes kept in sync by triggers created in the initial migration. `services/search/service.py::global_search()` already composes results from both, plus Secrets, for `/search` and the ⌘K command palette — the precedent this ADR follows for how a composition layer sits above per-feature search without owning its own index.

Separately, Phase 07 needs a tag vocabulary for Notes and Documents. Tags already exist for Secrets (`tags` + `secret_tag_links`), and the same "extend vs. duplicate" question applies there.

## 2. Decision

**Knowledge Hub extends the existing FTS5 infrastructure. It introduces no new search index, no new content table, and no parallel search implementation.**

`services/knowledge/service.py::list_knowledge()` delegates its text-query path to the existing `notes_service.search_notes()` and `documents_service.search_documents()` — the same functions `/search` already calls — rather than issuing its own `MATCH` SQL against `notes_fts`/`documents_fts` or creating a third index. When no query is present, the Hub lists by `updated_at DESC` via ordinary (non-FTS) queries, matching how both feature services already behave outside their search paths.

**`/search`, `GET /api/search`, and the ⌘K command palette are unchanged by this phase — same route, same parameters, same response shape, including their existing coverage of Secrets.** [ADR-0007](0007-search-dedicated-page.md) §6 states its accepted scope "remains exactly §2: a `/search` results page reusing the existing `GET /api/search` endpoint" and directs that it not be expanded "without a new decision." This ADR is not that new decision — it does not touch `/search` at all. Knowledge Hub is a distinct new route, `/knowledge`, with its own endpoint, `GET /api/knowledge`, answering a different question ("browse and organize what I know" vs. "find this thing now"). Both existing per [`01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.7 ("one search") is preserved: there remains exactly one search implementation per index — the Hub queries the same two FTS5 indexes through the same two functions `/search` already uses, rather than growing a second implementation of "search notes" or "search documents."

**Tagging follows the same reuse principle.** Two new link tables, `note_tag_links` and `document_tag_links`, both reference the **existing** `tags` table — mirroring the shipped `secret_tag_links` pattern exactly. One shared tag vocabulary across Secrets, Notes, and Documents; no new taxonomy, no modification to `secret_tag_links` or any Secrets behavior.

## 3. Alternatives considered

- **A new Knowledge Hub-specific search index** (e.g. a unified `knowledge_fts` covering notes + documents in one table) — rejected: would require its own sync triggers duplicating logic `notes_fts`/`documents_fts` already implement correctly, and could drift from the two sources of truth it would be shadowing. No capability gap justifies the duplication — `list_knowledge()` can compose two search calls exactly as `global_search()` already does.
- **Evolve `/search` into the Hub** (extend `GET /api/search` with tag/type/project filters and repoint it at a knowledge-browsing UI) — rejected: directly contradicts ADR-0007 §6's explicit "not expanded without a new decision" and would drag Secrets into a knowledge-browsing surface, which [`01_SPEC.md`](../implementation/Phase-07-Knowledge-Hub/01_SPEC.md) §5 excludes on security-posture grounds (credentials are not knowledge).
- **Build the Hub *and* extend `GET /api/search`** with tag/type filters so the palette benefits too — rejected: `GET /api/search` is a shared contract consumed by both `/search` and the command palette; changing it puts two shipped, frozen-adjacent surfaces at regression risk to benefit one new one, for a benefit (tag-filtered palette results) nothing has asked for.
- **A separate `knowledge_tags` taxonomy**, independent of Secrets' `tags` table — rejected: would force the user to maintain two vocabularies where "client-a" as a Secret tag and "client-a" as a Note tag are different rows, which is the opposite of the "consistent tagging" the Phase 07 objective names.
- **Generalize `secret_tag_links` into one polymorphic `taggables` table** — rejected for now: the cleanest long-term shape, but it requires migrating shipped `secret_tag_links` data and altering a frozen phase's schema for a benefit (avoiding a third near-identical link table) that is small today. Revisit if a third taggable type ever appears.

## 4. Consequences

- `services/knowledge/` has zero search-implementation code of its own — it is purely a composition and aggregation layer, the same architectural shape `services/search/` already establishes. A future fix or tuning change to either FTS5 setup benefits the Hub automatically, with no duplicate fix required.
- `03_ARCHITECTURE.md` §4's Knowledge Hub open question is closed: extend, not duplicate. That line item should be checked off and pointed at this ADR.
- `/search`, `GET /api/search`, and the command palette carry zero risk from this phase — they are not modified, not imported by the new code, and not tested differently than before. ADR-0007 remains fully in force, unmodified and unsuperseded.
- Notes and Documents gain a new column-free way to be searched together, without either feature's own model, endpoint, or FTS trigger changing.
- Tagging is unified across Secrets, Notes, and Documents through one shared `tags` table, at the cost of two new link tables rather than zero — an accepted, small, additive cost.
- Forecloses (for now) a unified cross-content search index if one is ever needed for a reason beyond Notes+Documents aggregation (e.g. if a future phase wants ranked relevance across types). Revisit only if that concrete need materializes; two composed queries are sufficient for Phase 07's scope.

## 5. Cross-references

- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [0007-search-dedicated-page.md](0007-search-dedicated-page.md)
- [../implementation/Phase-07-Knowledge-Hub/01_SPEC.md](../implementation/Phase-07-Knowledge-Hub/01_SPEC.md)
- [../implementation/Phase-07-Knowledge-Hub/04_DATABASE.md](../implementation/Phase-07-Knowledge-Hub/04_DATABASE.md)
