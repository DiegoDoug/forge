# Prompt Studio — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved alongside [`03_BACKEND.md`](03_BACKEND.md) 2026-07-22.
> **Last Updated:** 2026-07-22

---

## 1. Endpoints

All routes are mounted under `router = APIRouter(prefix="/prompts", tags=["prompt-studio"], dependencies=[AuthDep])` (reachable as `/api/prompts/...` once aggregated in `app/api/router.py`, matching every other feature router's `AuthDep`-gated pattern — e.g. `project_init.py`'s `router = APIRouter(prefix="/project-init", ...)`).

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| `GET` | `/api/prompts` | query: `search?: str`, `tag?: str` | `200 PromptListOut` (array of lightweight list items) | session required |
| `POST` | `/api/prompts` | `PromptCreate` | `201 PromptOut` | session required |
| `GET` | `/api/prompts/{id}` | — | `200 PromptOut` / `404` | session required |
| `PATCH` | `/api/prompts/{id}` | `PromptUpdateMeta` | `200 PromptOut` / `404` / `422` | session required |
| `PUT` | `/api/prompts/{id}/content` | `PromptUpdateContent` | `200 PromptOut` / `404` / `422` | session required |
| `DELETE` | `/api/prompts/{id}` | — | `204` / `404` | session required |
| `POST` | `/api/prompts/{id}/duplicate` | — | `201 PromptOut` (the new prompt) / `404` | session required |
| `GET` | `/api/prompts/{id}/versions` | — | `200 PromptVersionListOut` / `404` | session required |
| `GET` | `/api/prompts/{id}/versions/{version_id}` | — | `200 PromptVersionOut` / `404` | session required |
| `POST` | `/api/prompts/{id}/versions/{version_id}/restore` | — | `200 PromptOut` (the prompt, now at its new current content) / `404` | session required |

No endpoint in this phase makes an outbound network call or accepts a provider/API-key parameter, per [`01_SPEC.md`](01_SPEC.md) §5.

## 2. Schemas

All in `backend/app/schemas/prompt_studio.py`:

- `PromptVariableIn` / `PromptVariableOut` — `name: str` (pattern `^[A-Za-z_][A-Za-z0-9_]{0,63}$`), `type: Literal["string", "number", "boolean"]`, `required: bool`, `default: str | float | bool | None`, `description: str | None` (≤500 chars). A model validator rejects duplicate `name`s within the same list and caps the list at 50 entries (per [`01_SPEC.md`](01_SPEC.md) §3.3).
- `PromptCreate` — `name: str` (1–200 chars), `description: str | None` (≤1000), `body: str` (1–20,000 chars), `variables: list[PromptVariableIn] = []`, `tags: list[str] = []` (≤10 tags, each ≤30 chars). A model validator calls `templating.extract_placeholders(body)` and rejects (422) if any extracted name is not present in `variables` (per [`01_SPEC.md`](01_SPEC.md) §3.4).
- `PromptUpdateMeta` — `name: str | None`, `description: str | None`, `tags: list[str] | None` — same field constraints as `PromptCreate`; omitted fields leave the existing value unchanged (partial update).
- `PromptUpdateContent` — `body: str`, `variables: list[PromptVariableIn]` — same placeholder-vs-variable validator as `PromptCreate`.
- `PromptOut` — `id, name, description, body, variables: list[PromptVariableOut], tags: list[str], version_number, created_at, updated_at`.
- `PromptListItemOut` — `id, name, description, tags, version_number, updated_at` (no `body`/`variables` — kept lightweight per [`03_BACKEND.md`](03_BACKEND.md) §2, matching why `04_DATABASE.md` calls out the list-vs-detail shape split).
- `PromptListOut` — `{"items": list[PromptListItemOut]}`.
- `PromptVersionOut` — `id, version_number, body, variables: list[PromptVariableOut], note, created_at`.
- `PromptVersionListItemOut` — `id, version_number, note, created_at` (no `body`/`variables` — same lightweight-list rationale).
- `PromptVersionListOut` — `{"items": list[PromptVersionListItemOut]}`.

No response schema exposes a SQLModel ORM instance directly, per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §1.1.

## 3. Error handling

Uses the existing centralized exception handling in `backend/app/core/errors.py` unmodified — no new error envelope shape is introduced. All errors return the existing `{"error": {"code", "message", "details"?}}` envelope.

| Case | Status | Mechanism |
|---|---|---|
| Prompt id doesn't exist | `404` | `service.py` raises the existing `NotFoundError` (`code: "not_found"`) |
| Version id doesn't exist, or exists but belongs to a different prompt | `404` | `service.py` raises `NotFoundError` — deliberately the same status/code as "doesn't exist at all," so a crafted URL mixing one prompt's id with another prompt's version id learns nothing beyond "not found" |
| `name`/`body`/`description`/`tags` violate length/count constraints | `422` | Pydantic schema validation (`RequestValidationError` → existing `validation_error` handler) |
| A `${name}` in `body` is not a declared variable | `422` | Pydantic model validator on `PromptCreate`/`PromptUpdateContent` raises inside validation, surfaced the same way as any other 422 — not a bespoke error code, so the frontend's existing 422-handling path (inline field errors via `react-hook-form` + `zod`) requires no special-casing |
| Variable `name` invalid pattern, duplicate name, or >50 variables | `422` | Pydantic schema validation on `PromptVariableIn`/the list |
| At least one output constraint from the whole PromptCreate/Update payload fails | `422` | same `validation_error` envelope, `details` carries the Pydantic error list (matching the existing handler's behavior exactly — no new shape) |

No `409 Conflict` case exists in this phase — there is no concurrent-edit detection (matching the rest of the app's precedent: last write wins, no optimistic-locking `ConflictError` usage exists anywhere yet either).

## 4. Rate limiting / abuse considerations

None beyond the existing deployment-level posture in [`../../../docs/Security.md`](../../../docs/Security.md) — every route in this phase only reads/writes the local SQLite database behind the existing session-auth dependency; there is no outbound call to rate-limit or budget, unlike the concern this section exists to flag for Model Playground/Prompt Studio in general (per this file's own template note). That concern is explicitly deferred along with the rest of live-execution scope — see [`01_SPEC.md`](01_SPEC.md) §5.

## 5. TODO

- [ ] None — this document is filled in for the specification review pass.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
