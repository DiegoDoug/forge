# Model Playground — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Confirmed — filled in against [03_BACKEND.md](03_BACKEND.md).
> **Last Updated:** 2026-07-29

---


## 1. Endpoints

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| GET | `/api/model-playground/providers` | — | `{ items: ProviderAvailability[] }` | session required |
| POST | `/api/model-playground/credentials` | `ProviderCredentialIn` | `ProviderCredentialOut` | session required |
| GET | `/api/model-playground/credentials` | — | `{ items: ProviderCredentialOut[] }` | session required |
| DELETE | `/api/model-playground/credentials/{id}` | — | 204 No Content | session required |
| POST | `/api/model-playground/runs` | `PlaygroundRunIn` | `PlaygroundRunOut` | session required |
| GET | `/api/model-playground/runs` | `?limit`, `?offset` | `{ items: PlaygroundRunListItem[] }` | session required |
| GET | `/api/model-playground/runs/{id}` | — | `PlaygroundRunOut` | session required |
| DELETE | `/api/model-playground/runs/{id}` | — | 204 No Content | session required |

All routes sit under `AuthDep`, same as every other feature router (per [`../../../docs/Security.md`](../../../docs/Security.md) "Authentication").

## 2. Schemas

New Pydantic schemas in `backend/app/schemas/model_playground.py` (never expose the SQLModel ORM objects directly, per [`03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §1.1):

- `ProviderAvailability`: `{ provider: str, display_name: str, configured: bool, models: list[str] }`
- `ProviderCredentialIn`: `{ provider: str, label: str | None, api_key: str }` — `api_key` is write-only input, never echoed in any response schema.
- `ProviderCredentialOut`: `{ id: str, provider: str, label: str, created_at: datetime, updated_at: datetime }` — deliberately has no `api_key` field at all (per spec FR3).
- `RunTargetIn`: `{ provider: str, model: str }`
- `PlaygroundRunIn`: `{ prompt: str, targets: list[RunTargetIn] }`
- `PlaygroundResultOut`: `{ id: str, provider: str, model: str, status: Literal["success","error","timeout"], response_text: str | None, error_message: str | None, latency_ms: int | None, prompt_tokens: int | None, completion_tokens: int | None }`
- `PlaygroundRunOut`: `{ id: str, prompt: str, created_at: datetime, results: list[PlaygroundResultOut] }`
- `PlaygroundRunListItem`: `{ id: str, prompt_excerpt: str, providers: list[str], created_at: datetime }` — `prompt_excerpt` is the prompt truncated server-side (e.g. 120 chars) so the history list payload stays small.

## 3. Error handling

| Case | Status | Notes |
|---|---|---|
| `targets` empty or exceeds the per-run cap (§4) | 400 | Pydantic/`ValidationError`-style rejection before any outbound call |
| A target's `provider` has no configured credential | 400 | Same — validated before dispatch, per `03_BACKEND.md` §2 |
| Unknown `provider` or `model` not in that provider's supported list | 400 | |
| Credential/run `id` not found | 404 | `NotFoundError`, same pattern as `services/secrets/service.py` |
| A single target's outbound call fails or times out | **200**, not an HTTP error | Surfaces as `status: "error"`/`"timeout"` on that result row — a partial failure is a normal, successful response for the run as a whole (per spec FR7) |
| Any unexpected server error | 500 | Generic `internal_error` envelope, full exception logged server-side only — per [`../../../docs/Security.md`](../../../docs/Security.md) "Input handling" |

## 4. Rate limiting / abuse considerations

Per [`../../../docs/Security.md`](../../../docs/Security.md)'s existing posture (no app-level rate limiting; a self-hosted, typically LAN-only or single-operator tool relies on the deployment's own reverse proxy/VPN for that), no new rate-limiting mechanism is introduced. Two defensive caps exist instead, to bound how much a single request can fan out:

- **Max targets per run: 6** (proposed — one per model across both v1 providers is well under this; leaves headroom without allowing an unbounded fan-out from one request). Enforced server-side (400 if exceeded) and reflected in the UI by disabling further selection past the cap.
- **Per-call timeout: 60s** (per ADR-0010 §2.5) bounds worst-case total request time to ~60s regardless of target count, since calls run concurrently, not sequentially (per `03_BACKEND.md` §2).

## 5. TODO

- [ ] Assign a phase owner.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
