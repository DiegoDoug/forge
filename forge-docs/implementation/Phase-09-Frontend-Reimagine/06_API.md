# Frontend Reimagine — API

> **Purpose:** State this phase's API impact and enumerate the frontend-facing contracts it must preserve.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved 2026-08-06; holds as implemented — every contract in this document re-verified unchanged at T28/RC.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [03_BACKEND.md](03_BACKEND.md)

---

## 1. API impact: none

**No endpoint is added, removed, renamed, or reshaped.** All 112 endpoints keep their path, method, request body, response body, status codes, and error contract.

| Module | Endpoints | Module | Endpoints |
|---|---|---|---|
| crypto | 15 | knowledge | 7 |
| secrets | 13 | projects | 7 |
| prompt_studio | 10 | auth | 6 |
| model_playground | 9 | notes | 5 |
| generators | 8 | project_init | 5 |
| documents | 7 | settings | 4 |
| ingest | 7 | health | 3 |
| | | workbench | 3 |
| | | converters | 2 |
| | | search | 1 |

## 2. The frontend API layer

`lib/api-client.ts` remains the single fetch boundary, with its typed `ApiError` (`status`, `code`, `message`, `details`), its `credentials: "include"`, its 204 handling, and its JSON/text content-type branching. **Unchanged.**

Each `features/*/api.ts` remains the only file in its feature that knows endpoint shapes. **Unchanged.** No query key is renamed, since renaming one silently breaks cache invalidation across mutations.

### 2.1 Boundary violations before and after

| | Before | After |
|---|---|---|
| Raw `fetch` for a JSON GET, bypassing `api-client` | **1** — `settings/page.tsx:23` → `fetch("/system/status")` | **0** |
| Raw `fetch` for binary download (legitimate — needs the blob, not JSON) | 2 — `documents/api.ts:94`, `project-init/api.ts:106` | 2, unchanged |

The Settings bypass is removed as part of FR14. The two binary-download fetches are correct as written: they need the raw `Response` for blob handling, which `api-client`'s JSON-oriented wrapper does not provide. They stay.

## 3. Contracts that must survive the redesign

This is the regression surface. Each line is re-tested in T28 against the pre-phase baseline.

### 3.1 Route parameters

| Param | Routes | Behavior |
|---|---|---|
| `?open=<id>` | `/secrets`, `/notes`, `/documents`, `/prompt-studio` | Opens the detail sheet/editor over the list without leaving the route. Removed by navigating to the bare route. |
| `?project_id=<id>` | `/secrets`, `/notes`, `/documents`, `/knowledge` | Initial scope, read once on mount into local state. |
| `?new=1` | `/secrets`, `/notes`, `/projects` | Consumed exactly once via a `useRef` guard, then stripped with `router.replace`. Must not re-fire on refresh or back-navigation. |
| `?tab=<name>` | `/developer-toolkit` | `generators\|crypto\|utilities`; unknown values fall back to `generators`. Switching uses `router.replace(..., { scroll: false })`. **External contract** — three redirects target it. |
| `?q=<query>` | `/search`, `/knowledge` | `/search`: synced via `router.replace`, 2-character threshold. `/knowledge`: one of four filters. |
| `?type=<t>` | `/knowledge` | `all\|note\|document`. |
| `?tag_id=<id>` | `/knowledge` | **Repeatable** — `getAll`/`append`, not `get`/`set`. |

### 3.2 Redirects (`next.config.ts`) — all `permanent: false`

| From | To | Origin |
|---|---|---|
| `/vault` | `/secrets` | [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md) |
| `/ingest` | `/converters` | Phase 04 |
| `/generators` | `/developer-toolkit?tab=generators` | Phase 08 |
| `/crypto` | `/developer-toolkit?tab=crypto` | Phase 08 |
| `/utilities` | `/developer-toolkit?tab=utilities` | Phase 08 |

None is added, removed, or changed. T13 adds one **rewrite** (not a redirect) for `/system/status`.

### 3.3 Behavioral contracts

| Behavior | Where | Must not change |
|---|---|---|
| Optimistic layout update | `features/workbench/api.ts` | `onMutate` snapshot, `onError` rollback, `onSettled` invalidate — **and** the rule that panel types absent from this build survive unrelated user actions. |
| Autosave debounce | `app/(app)/documents/page.tsx` | 600ms, patch-shaped (`{title}` or `{content}`, not the whole document). |
| Ingest job polling | `app/(app)/converters/page.tsx` | `refetchInterval` 800ms while `status === "processing"`, `false` otherwise. |
| Search gating | palette + `/search` | Query enabled only when trimmed length > 1. |
| Secret edit reveal | `app/(app)/secrets/page.tsx` | `getSecret(id, true)` before opening the edit dialog. |
| Auth redirects | `features/auth/auth-gate.tsx` | Not-set-up → `/setup`; 401 or `setup_required` → `/unlock`; unlock success → `/`. |
| Prompt create workaround | `app/(app)/prompt-studio/page.tsx` | `body: " "` — the schema enforces `min_length=1`. |
| Theme sync | `app/(app)/settings/page.tsx` | `setTheme` locally **and** `settingsApi.updateTheme` server-side. |

## 4. Cross-references

- [03_BACKEND.md](03_BACKEND.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) §3 · [00_AUDIT.md](00_AUDIT.md)
- [../../../docs/API.md](../../../docs/API.md)
