# Knowledge Hub — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04)
> **Status:** Confirmed — `01_SPEC.md` §7's four open questions resolved 2026-08-04; ready for implementation pending final review
> **Last Updated:** 2026-08-04

---

## 1. Service boundary

A **new** subpackage: `backend/app/services/knowledge/`.

New rather than an extension, because the Hub's job — aggregating across two feature services — belongs to neither of them. Putting cross-feature aggregation inside `services/notes/` or `services/documents/` would make one feature depend on the other, which `03_ARCHITECTURE.md` §2 forbids. This mirrors how `services/search/` already sits above `notes`/`documents`/`secrets` as a composition layer.

Related existing backend code (**actual current paths** — the scaffold previously listed `backend/app/notes/` etc., which do not exist):

- `backend/app/services/notes/service.py` — `search_notes()` (FTS5), CRUD
- `backend/app/services/documents/service.py` — `search_documents()` (FTS5), CRUD, `export.py`
- `backend/app/services/search/service.py` — `global_search()`, the existing composition-layer precedent
- `backend/app/services/ingest/` — transient job pipeline, no database
- `backend/app/models/note.py`, `document.py`, `secrets.py` (`Tag`, `SecretTagLink`)

Planned files:

```
backend/app/services/knowledge/
  __init__.py
  service.py      # query/aggregation, tag assignment, link management
```

## 2. Business logic

`service.py` owns:

- **`list_knowledge(session, *, q, item_type, tag_ids, project_id)`** — the Hub query (`01_SPEC.md` FR1–FR6). Composes results from the two feature services, normalizes them into one `KnowledgeItem` shape (type, id, title, excerpt, tags, project_id, updated_at), applies **AND** tag/project filters (§6.8), sorts by `updated_at DESC`, and caps the returned page at the fixed module constant `KNOWLEDGE_RESULT_LIMIT = 100` (`01_SPEC.md` §6.6) — not a caller-supplied parameter, so there is no way to request more than 100 or to page past the cap. Returns the capped items plus the true, uncapped `total` match count and a `truncated` flag, matching `06_API.md` §1.1a exactly.
- **`list_knowledge_tags(session)`** — tags in use by knowledge items, with counts (FR12).
- **`add_tag(session, item_type, item_id, tag_name_or_id)`** — assign, creating the tag if the name is new (FR10). Reuses the existing `tags` row when the name already exists.
- **`remove_tag(session, item_type, item_id, tag_id)`** — unassign only; never deletes the tag (FR11).
- **`list_links(session, item_type, item_id)`** — links from both sides, returned as one list (FR15).
- **`create_link(session, source, target)`** — validates not-self and not-duplicate-in-either-direction, normalizes the pair, inserts (FR18).
- **`delete_link(session, link_id)`** — (FR16).
- **`purge_links_for(session, item_type, item_id)`** — removes every link referencing a deleted item (FR17).

### 2.1 Full-text search delegation

`list_knowledge` does **not** write its own FTS5 SQL. When `q` is present it calls the existing `notes_service.search_notes()` and `documents_service.search_documents()`, exactly as `services/search/service.py` already does. This keeps one FTS implementation per index (`01_SPEC.md` §6.4) and means a future fix to either feature's search benefits the Hub automatically.

When `q` is absent the Hub lists by `updated_at DESC` via ordinary queries — the FTS path is only for text queries, matching how both feature services already behave.

### 2.2 Delete-hook integration (FR17)

Deleting a Note or Document must purge its links. Two options, to be settled at implementation time:

1. The Hub exposes `purge_links_for()` and `notes/service.py` / `documents/service.py` call it in their delete paths.
2. The Hub subscribes to nothing and the route layer orchestrates delete-then-purge.

**Preferred: option 1**, but note it makes `notes`/`documents` import from `knowledge`. That is the *composition layer being imported by a feature*, the reverse of the usual direction, and it is worth a second look during T4 — if it reads as a cross-feature import, option 2 (orchestrate in the router, keeping services independent) is the fallback. Flagged rather than silently decided; `07_TESTING.md` §1 tests the behavior either way.

## 3. Integration with existing services

| Service | How the Hub uses it | Does it change? |
|---|---|---|
| `services/notes/` | Calls `search_notes()`, reads `Note` rows | No — except possibly the delete path, §2.2 |
| `services/documents/` | Calls `search_documents()`, reads `Document` rows | No — except possibly the delete path, §2.2 |
| `services/secrets/` | Not used at all | No |
| `services/search/` | Not used, not modified | **No** — hard requirement, `01_SPEC.md` FR21 |
| `services/ingest/` | Not used, not modified | No |
| `services/projects/` | Not called; the Hub reads the existing `project_id` column directly | No |

## 4. Architectural compliance

- [x] Routers stay thin — all logic lives in `services/knowledge/` (per `03_ARCHITECTURE.md` §2).
- [x] No cross-feature imports between `notes` and `documents`; the Hub composes them, the way `search` already does. §2.2's delete hook is the one place this needs a deliberate check.
- [x] No new external dependency — stdlib, SQLModel, and existing services only. Nothing to add to `06_TECH_STACK.md`.
- [x] Pydantic schemas mediate every response; no ORM object is returned directly (`03_ARCHITECTURE.md` §1.1). New schemas live in `backend/app/schemas/knowledge.py`.
- [x] Schema changes ship as an explicit Alembic migration (`04_DATABASE.md` §3).
- [x] No outbound network calls, no provider/credential concept — nothing for `docs/Security.md` to review beyond the existing session-auth requirement on every route.

## 5. Activity logging

Notes/Documents/Projects already record activity via `services/activity.py`. Tag assignment and link creation are user-visible mutations of the same kind. **Proposed:** log link create/delete and tag assign/unassign as activity events, matching existing convention. Confirm during implementation against how `activity.py` classifies actions — if the existing `ActivityAction` enum has no fitting member, adding one is an additive change, but it should be a conscious choice, not an accident.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
