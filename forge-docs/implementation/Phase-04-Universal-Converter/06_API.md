# Universal Converter — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — filled in against [`03_BACKEND.md`](03_BACKEND.md), pending owner review.
> **Last Updated:** 2026-07-23

---

## 1. Endpoints

### 1.1 New (additive only)

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| GET | `/api/converters/providers` | — | `{"providers": [{"slug": str, "label": str, "input_extensions": [str], "output_format": str}]}` | session required |

### 1.2 Existing — unchanged, kept for backward compatibility

Per [`01_SPEC.md`](01_SPEC.md) requirement 5 (no breaking API changes), every endpoint below keeps its current path, request shape, response shape, and behavior exactly as-is. None are removed, renamed, or reimplemented — they continue to be served by the exact same router/service code that exists today.

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/converters/cron/parse` | session required |
| GET | `/api/ingest/formats` | session required |
| POST | `/api/ingest/jobs` | session required |
| GET | `/api/ingest/jobs/{job_id}` | session required |
| GET | `/api/ingest/jobs/{job_id}/files/{file_id}/download` | session required |
| GET | `/api/ingest/jobs/{job_id}/files/{file_id}/content` | session required |
| GET | `/api/ingest/jobs/{job_id}/download` | session required |
| POST | `/api/ingest/jobs/{job_id}/files/{file_id}/save-to-notes` | session required |

`GET /api/converters/providers` is a superset view for the unified frontend page (so it can render "Documents" section format info from the same registry the backend uses — see [`01_SPEC.md`](01_SPEC.md) requirement 7) — it does not replace `GET /api/ingest/formats`, which keeps working identically for any existing caller.

## 2. Schemas

New Pydantic response schema only (request has no body):

```python
# backend/app/schemas/converters.py — addition alongside existing CronParseIn/CronParseOut
class ProviderOut(BaseModel):
    slug: str
    label: str
    input_extensions: list[str]
    output_format: str

class ProvidersOut(BaseModel):
    providers: list[ProviderOut]
```

No existing schema (`CronParseIn`, `CronParseOut`, any Ingest response shape) is modified.

## 3. Error handling

`GET /api/converters/providers` has no error cases beyond the standard cross-cutting ones already handled globally: `401 unauthorized` (no/invalid session, via the existing `AuthDep`) and `500 internal_error` (unexpected exception, via the existing global handler). It performs no I/O beyond reading an in-memory list, so there is no validation-error or not-found case to define.

Every existing endpoint's error handling (file-too-large, empty-file, unsupported-format, job-not-found, file-not-ready) is unchanged — see `docs/Security.md` and the current `api/routes/ingest.py` implementation for the existing cases, none of which this phase touches.

## 4. Rate limiting / abuse considerations

No change to the existing posture. This phase adds no new upload surface, no new outbound network call, and no new persistence — the abuse surface is identical to today's Converters + Ingest combined, which is already covered by `docs/Security.md`'s existing file size/count caps and the documented deployment-level rate-limiting stance (VPN/reverse-proxy, not built-in, per that doc's "Things intentionally out of scope").

## 5. TODO

- [ ] Project-owner review of the new `/api/converters/providers` endpoint shape alongside [`03_BACKEND.md`](03_BACKEND.md)'s provider interface design.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
