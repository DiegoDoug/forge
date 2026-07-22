# Project Initialization Engine — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted.
> **Last Updated:** 2026-07-22

---

## 1. Endpoints

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| GET | `/api/project-init/catalog` | — | `TemplateCatalogOut` | session required |
| POST | `/api/project-init/generate` | `GenerateRequest` | `201 GenerationOut` | session required |
| GET | `/api/project-init/history?limit=20` | — | `GenerationListOut` | session required |
| GET | `/api/project-init/{id}/download` | — | `200` zip binary | session required |
| DELETE | `/api/project-init/{id}` | — | `204` | session required |

All routes sit behind the same session-cookie auth dependency (`app.api.deps`) as every other `/api/*` route — no new auth model, per [`03_ARCHITECTURE.md §1.3`](../../03_ARCHITECTURE.md).

### `GET /api/project-init/catalog`

**Response 200:**
```json
{
  "kinds": [
    {
      "kind": "fdk_phase",
      "label": "FDK Phase Scaffold",
      "description": "Generate a new Phase-XX-Name/ folder matching Forge's own FDK structure.",
      "fields": [
        {"name": "phase_number", "type": "integer", "required": true, "min": 1},
        {"name": "phase_name", "type": "string", "required": true, "max_length": 80},
        {"name": "objective", "type": "string", "required": true, "max_length": 500}
      ],
      "output_files": ["README.md", "CURRENT_STATE.md", "01_SPEC.md", "02_UI.md", "03_BACKEND.md", "04_DATABASE.md", "05_COMPONENTS.md", "06_API.md", "07_TESTING.md", "08_ACCEPTANCE.md", "09_IMPLEMENTATION_TASKS.md", "10_RELEASE_NOTES.md", "IMPLEMENT.md"]
    },
    {
      "kind": "ai_instructions",
      "label": "AI Project Instructions",
      "description": "Generate CLAUDE.md / AGENTS.md / instructions.md for any project.",
      "fields": [
        {"name": "project_name", "type": "string", "required": true, "max_length": 80},
        {"name": "description", "type": "string", "required": true, "max_length": 1000},
        {"name": "tech_stack", "type": "string[]", "required": false, "max_items": 20},
        {"name": "conventions", "type": "string", "required": false, "max_length": 4000},
        {"name": "output_files", "type": "string[]", "required": true, "enum": ["CLAUDE.md", "AGENTS.md", "instructions.md"], "min_items": 1}
      ],
      "output_files": null
    }
  ]
}
```

### `POST /api/project-init/generate`

**Request:**
```json
{ "kind": "fdk_phase", "config": { "phase_number": 9, "phase_name": "Knowledge Hub", "objective": "Unify Notes, Documents, and Ingest output into one searchable knowledge base." } }
```

**Response 201** (`GenerationOut`):
```json
{ "id": "…", "kind": "fdk_phase", "name": "Knowledge Hub", "created_at": "2026-07-22T…", "file_count": 13 }
```

The zip itself is fetched immediately after via `GET /api/project-init/{id}/download` (frontend triggers both calls in sequence — see [05_COMPONENTS.md](05_COMPONENTS.md)), keeping this endpoint's response small and JSON (consistent with `api-client.ts`'s JSON-first `request<T>` helper) rather than mixing a binary body into the creation response.

### `GET /api/project-init/history`

**Response 200** (`GenerationListOut`):
```json
{ "items": [ { "id": "…", "kind": "fdk_phase", "name": "Knowledge Hub", "created_at": "2026-07-22T…" } ] }
```

### `GET /api/project-init/{id}/download`

Re-renders from the stored `config` and streams the zip. **Response 200:** `Content-Type: application/zip`, `Content-Disposition: attachment; filename="Phase-09-Knowledge-Hub.zip"` (fdk_phase) or `"acme-api-ai-instructions.zip"` (ai_instructions) — sanitized filenames, same pattern as `services/documents/export.py`'s `safe_filename`.

### `DELETE /api/project-init/{id}`

**Response 204.**

## 2. Schemas

New Pydantic schemas in `backend/app/schemas/project_init.py` (request/response shapes only — the ORM model `ProjectInitGeneration` is never returned directly, per [`03_ARCHITECTURE.md §1.1`](../../03_ARCHITECTURE.md)):

- `FieldSpec` — `{name, type, required, max_length?, min?, max_items?, min_items?, enum?}`.
- `TemplateKindOut` — `{kind, label, description, fields: list[FieldSpec], output_files: list[str] | None}`.
- `TemplateCatalogOut` — `{kinds: list[TemplateKindOut]}`.
- `FdkPhaseConfig` — `{phase_number: int, phase_name: str, objective: str}`.
- `AiInstructionsConfig` — `{project_name: str, description: str, tech_stack: list[str] = [], conventions: str = "", output_files: list[Literal["CLAUDE.md","AGENTS.md","instructions.md"]]}`.
- `GenerateRequest` — `{kind: Literal["fdk_phase","ai_instructions"], config: dict}` — the nested `config` is validated against `FdkPhaseConfig`/`AiInstructionsConfig` inside the service layer based on `kind` (a discriminated-union validator), not accepted as a raw untyped dict past that point.
- `GenerationOut` — `{id: str, kind: str, name: str, created_at: datetime, file_count: int}`.
- `GenerationListOut` — `{items: list[GenerationOut minus file_count]}`.

## 3. Error handling

| Case | Status | Notes |
|---|---|---|
| Missing/invalid required field | 422 | Standard FastAPI/Pydantic validation error, app-wide error envelope. |
| `ai_instructions` with empty `output_files` | 422 | Enforced by `min_items=1` on the schema. |
| Unknown `kind` | 422 | Rejected by the `Literal` type on `GenerateRequest.kind`. |
| Generation/history id not found (download, delete) | 404 | `NotFoundError`, matching `services/notes/service.py`'s `_get_or_404` convention. |
| Unauthenticated request | 401 | Existing session dependency, unchanged. |

## 4. Rate limiting / abuse considerations

None beyond the existing deployment-level posture in [`../../../docs/Security.md`](../../../docs/Security.md). This endpoint set makes no outbound network calls and no filesystem writes outside the database — the only resource cost is a small in-memory zip and one SQLite row per generation, comparable to creating a Note. No new abuse surface is introduced.

## 5. TODO

None.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
