# Projects — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Confirmed
> **Last Updated:** 2026-08-02

---

## 1. Endpoints

All routes are session-authenticated (`dependencies=[AuthDep]`), matching every other feature router.

**New router: `backend/app/api/routes/projects.py`, prefix `/projects`**

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| GET | `/api/projects` | query: `archived: bool = false` | `list[ProjectSummaryOut]` | session required |
| POST | `/api/projects` | `ProjectCreateIn` | `ProjectOut` (201) | session required |
| GET | `/api/projects/{project_id}` | — | `ProjectOut` | session required |
| PATCH | `/api/projects/{project_id}` | `ProjectUpdateIn` | `ProjectOut` | session required |
| DELETE | `/api/projects/{project_id}` | — | 204 | session required |
| POST | `/api/projects/{project_id}/ai/run` | `ProjectAiRunIn` | `PlaygroundRunOut` (201, reused from `model_playground` schemas) | session required |
| GET | `/api/projects/{project_id}/ai/runs` | query: `limit: int = 20` | `PlaygroundRunListOut` (reused) | session required |

**Additive query params on existing endpoints** (no breaking change — new optional filter):

| Method | Path | New param |
|---|---|---|
| GET | `/api/secrets` | `project_id: str \| None` |
| GET | `/api/notes` | `project_id: str \| None` |
| GET | `/api/documents` | `project_id: str \| None` |

**Additive request fields** (all optional — existing clients unaffected):

| Schema | New field |
|---|---|
| `SecretCreateIn` / `SecretUpdateIn` | `project_id: str \| None` |
| `NoteCreateIn` / `NoteUpdateIn` | `project_id: str \| None` |
| `DocumentCreateIn` / `DocumentUpdateIn` | `project_id: str \| None` |

And the corresponding `*Out`/`*SummaryOut` schemas for Secrets/Notes/Documents each gain a `project_id: str | None` field so the frontend can render current assignment.

## 2. Schemas

`backend/app/schemas/projects.py` (new):

```
ProjectCreateIn: name (1-200, required), description (0-2000, default ""),
                 color (default "#6366f1"), default_provider (str|None),
                 default_model (str|None)
ProjectUpdateIn: same fields, all optional (exclude_unset semantics)
ProjectOut: id, name, description, color, archived, default_provider,
            default_model, secret_count, note_count, document_count,
            created_at, updated_at
ProjectSummaryOut: id, name, color, archived, secret_count, note_count,
                   document_count, updated_at   (lighter list shape, same
                   split ProjectOut/DocumentSummaryOut pattern Documents uses)
ProjectAiRunIn: prompt (1-20000, required — same bound as PlaygroundRunIn.prompt)
```

Validation: `default_provider`/`default_model` reuse the exact same provider/model membership check `model_playground/schemas.py` already defines (`_check_provider`, `_check_model`) — imported, not re-implemented, so the two never drift. A `model_validator` requires both-or-neither (setting a model without a provider, or vice versa, is a 422).

Never expose ORM objects directly (per `../../03_ARCHITECTURE.md` §1.1) — routes always return the `schemas/` shapes above.

## 3. Error handling

| Case | Status | Code |
|---|---|---|
| Project not found | 404 | `not_found` (existing `NotFoundError`) |
| Create/update with invalid name length | 422 | `validation_error` (existing handler) |
| `default_provider`/`default_model` not a real registry entry, or model not in that provider's catalogue | 422 | `validation_error` |
| Only one of `default_provider`/`default_model` set | 422 | `validation_error` |
| AI run requested with no default provider/model configured | 400 | `project_ai_not_configured` (new `AppError` subtype-equivalent, same pattern as Model Playground's `provider_not_configured`) |
| AI run requested against a configured default whose credential is missing | 400 | `provider_not_configured` (bubbles up unchanged from `runs.create_run`) |
| Unhandled exception | 500 | `internal_error` (existing global handler — never leaks internals) |

## 4. Rate limiting / abuse considerations

No additional consideration beyond the deployment-level posture in `../../../docs/Security.md` — the AI-run endpoint reuses Model Playground's existing per-call `TIMEOUT_SECONDS = 60.0` bound and its existing single-operator, session-gated exposure; it does not introduce a new unauthenticated or higher-volume surface (one prompt per call, same as Model Playground's own `/runs` endpoint, just addressed through a project rather than a raw target list).

## 5. TODO

None — this document is confirmed, not a template placeholder.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
