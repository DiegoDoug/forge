# Knowledge Hub — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04)
> **Status:** Confirmed — `01_SPEC.md` §7's four open questions resolved 2026-08-04; ready for implementation pending final review
> **Last Updated:** 2026-08-04

---

## 1. Endpoints

All routes live under `backend/app/api/routes/knowledge.py`, prefix `/knowledge`, and carry `dependencies=[AuthDep]` — session required, matching every other Forge feature router.

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| GET | `/api/knowledge` | query: `q`, `type`, `tag_id` (repeatable), `project_id` | `KnowledgeListOut` | session required |
| GET | `/api/knowledge/tags` | — | `list[KnowledgeTagOut]` | session required |
| POST | `/api/knowledge/{item_type}/{item_id}/tags` | `KnowledgeTagAssignIn` | `list[TagOut]` (item's tags after assignment) | session required |
| DELETE | `/api/knowledge/{item_type}/{item_id}/tags/{tag_id}` | — | `204` | session required |
| GET | `/api/knowledge/{item_type}/{item_id}/links` | — | `list[KnowledgeLinkOut]` | session required |
| POST | `/api/knowledge/{item_type}/{item_id}/links` | `KnowledgeLinkCreateIn` | `KnowledgeLinkOut` (`201`) | session required |
| DELETE | `/api/knowledge/links/{link_id}` | — | `204` | session required |

`{item_type}` is constrained to `note` \| `document` by an enum, so an unknown type is a `422`, not a lookup miss.

**Unchanged by this phase:** `GET /api/search` keeps its exact current path, parameters, and response shape (`{secrets, notes, documents}`). `01_SPEC.md` FR21 makes this a hard requirement; `08_ACCEPTANCE.md` AC21 verifies it.

### 1.1 `GET /api/knowledge`

Query parameters — **exactly these four, nothing else.** There is no `page`, `offset`, `cursor`, or `limit` parameter: the response cap is a fixed server-side constant (§1.1a), not client-configurable, so the API surface cannot be mistaken for pagination support that does not exist.

| Name | Type | Default | Meaning |
|---|---|---|---|
| `q` | str | `""` | Full-text query. Empty means "no text filter" — list by recency. |
| `type` | `all` \| `note` \| `document` | `all` | Item type filter (FR3). |
| `tag_id` | str, repeatable | none | **AND semantics, final** — an item must carry **every** listed `tag_id` to match (FR4, §6.8). There is no OR mode and none is planned. |
| `project_id` | str \| null | none | Reuses Phase 06 scoping (FR5). |

#### 1.1a Result cap — fixed at 100, no pagination

`GET /api/knowledge` returns **at most 100 items**, ordered by `updated_at` descending before the cap is applied — the cap always drops the least-recently-updated tail. The cap is a server-side constant (`KNOWLEDGE_RESULT_LIMIT = 100` in `services/knowledge/service.py`), not a request parameter. This phase has **no pagination anywhere** — this is the only mechanism for bounding the result set, per `01_SPEC.md` §6.6/§6.7.

Response (`KnowledgeListOut`):

```json
{
  "items": [
    {
      "type": "note",
      "id": "…",
      "title": "Q3 architecture notes",
      "excerpt": "We decided to keep the FTS5 index…",
      "tags": [ { "id": "…", "name": "client-a", "color": "#6366f1" } ],
      "project_id": "…",
      "updated_at": "2026-08-04T10:00:00Z"
    }
  ],
  "total": 137,
  "truncated": true
}
```

`items` never exceeds 100 entries. `total` is the real match count across the full (unbounded) query, computed independently of the 100-item cap — e.g. a `COUNT(*)` over the same filters, not `len(items)`. `truncated` is `true` exactly when `total > 100`. This is what lets the UI say "showing first 100 of 137" instead of silently cutting the list (`01_SPEC.md` §6.6, FR8a).

### 1.2 `GET /api/knowledge/tags`

Returns only tags actually assigned to a Note or Document, with counts (FR12):

```json
[ { "id": "…", "name": "client-a", "color": "#6366f1", "count": 12 } ]
```

A tag used only by Secrets does not appear here — it would be a filter that returns nothing.

### 1.3 Tag assignment

`POST /api/knowledge/{item_type}/{item_id}/tags` accepts either an existing tag id or a new tag name (FR10):

```json
{ "tag_id": "…" }
{ "name": "client-a", "color": "#6366f1" }
```

Exactly one of `tag_id` / `name` must be present — both or neither is a `422`. When `name` matches an existing tag case-insensitively, that tag is reused rather than duplicated (the `tags.name` unique constraint would reject a duplicate anyway; the service resolves it before insert so the user gets an assignment, not an error).

### 1.4 Links

`POST /api/knowledge/{item_type}/{item_id}/links`:

```json
{ "target_type": "document", "target_id": "…" }
```

Response (`KnowledgeLinkOut`) is always expressed **relative to the item you asked from**, so the frontend never has to work out which end it is on:

```json
{
  "link_id": "…",
  "other": {
    "type": "document",
    "id": "…",
    "title": "Deployment runbook"
  },
  "created_at": "2026-08-04T10:00:00Z"
}
```

## 2. Schemas

New Pydantic schemas in `backend/app/schemas/knowledge.py`. No ORM object is ever returned directly (`03_ARCHITECTURE.md` §1.1).

- `KnowledgeItemType` — `str, Enum`: `note` \| `document`
- `KnowledgeItemOut` — type, id, title, excerpt, tags, project_id, updated_at
- `KnowledgeListOut` — items, total, truncated
- `KnowledgeTagOut` — id, name, color, count
- `KnowledgeTagAssignIn` — tag_id \| name + optional color, with the exactly-one validator from §1.3
- `KnowledgeLinkCreateIn` — target_type, target_id
- `KnowledgeLinkOut` — link_id, other (type/id/title), created_at

`TagOut` is reused from `schemas/secrets.py` if its shape matches; otherwise a knowledge-local equivalent is defined rather than modifying the Secrets schema.

## 3. Error handling

| Case | Status | Code |
|---|---|---|
| Unknown `item_type` | 422 | FastAPI enum validation |
| Item id not found | 404 | `NotFoundError` (existing `core/errors.py`) |
| Link target not found | 404 | `NotFoundError` |
| Link to self | 400 | `knowledge_link_self` |
| Link already exists (either direction) | 409 | `knowledge_link_duplicate` |
| Tag assign with both/neither `tag_id` and `name` | 422 | validation |
| Tag not found on unassign | 404 | `NotFoundError` |
| No session | 401 | existing `AuthDep` behavior |

Errors reuse the existing `AppError`/`NotFoundError` machinery in `backend/app/core/errors.py` — no new error framework.

## 4. Rate limiting / abuse considerations

None beyond Forge's existing deployment-level posture (`docs/Security.md`). This phase:

- makes **zero outbound network calls**,
- introduces **no provider or API-key concept**,
- exposes **no credential material** — Secrets are excluded from the Hub's content model entirely (`01_SPEC.md` §5),
- adds no unauthenticated route.

Forge-wide rate limiting remains a tracked gap in `02_ROADMAP.md` §5, unchanged by this phase.

## 5. Documentation

`docs/API.md` must gain the seven routes above at implementation time (`09_IMPLEMENTATION_TASKS.md` T16).

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
