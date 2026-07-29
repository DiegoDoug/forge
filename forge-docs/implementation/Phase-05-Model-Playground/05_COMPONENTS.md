# Model Playground — Components

> **Purpose:** Frontend component inventory for this phase — what gets built, and what's reused from the existing design system.
> **Scope:** Component-level detail. Screen-level UX lives in 02_UI.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Confirmed — filled in against [02_UI.md](02_UI.md), [06_API.md](06_API.md).
> **Last Updated:** 2026-07-29

---


## 1. New components

All under `frontend/features/model-playground/`:

| Component | Responsibility |
|---|---|
| `provider-list.tsx` | Renders the two providers (openai, anthropic), configured/unconfigured state, wires up the credential dialog |
| `credential-form-dialog.tsx` | Add/replace a provider's API key (write-only field, no reveal) |
| `prompt-composer.tsx` | Prompt textarea + provider/model checkbox selection (capped at 6 targets, per `06_API.md` §4) + submit |
| `result-panel.tsx` | One panel per `PlaygroundResultOut` — loading/success/error/timeout states |
| `run-view.tsx` | Composes `prompt-composer` + a responsive grid of `result-panel`s for the active run |
| `run-history-list.tsx` | Past-runs list with prompt excerpt, provider badges, timestamp, delete action |

Page: `frontend/app/(app)/model-playground/page.tsx` — composes `provider-list` + `run-view` + `run-history-list`.

## 2. Reused components

- `components/ui/card.tsx`, `dialog.tsx`, `button.tsx`, `checkbox.tsx`, `textarea.tsx`, `skeleton.tsx`, `badge.tsx`, `alert-dialog.tsx` (delete confirmation, per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2), `sonner.tsx` (toast on credential save/delete).
- `components/empty-state.tsx` — history list's zero-runs state, and the providers list's zero-configured state.
- `components/page-header.tsx` — page title/description, consistent with every other feature page.
- `components/copy-button.tsx` — copy a result panel's response text.
- No new shared component is added to `components/` — everything net-new is specific enough to Model Playground to live in its own `features/` folder (per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1.5).

## 3. `features/` structure

- `frontend/features/model-playground/api.ts` — the only file that knows this phase's backend endpoint shapes (per [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1), mirroring `features/prompt-studio/api.ts`'s shape: typed request/response interfaces, a plain `modelPlaygroundApi` object of fetch calls, and exported `use*` hooks/mutations built on top of it.
- Component files as listed in §1.

## 4. State management

TanStack Query, cache keys under the `["model-playground", ...]` namespace:

| Hook | Query key | Invalidated by |
|---|---|---|
| `useProviders()` | `["model-playground", "providers"]` | credential create/replace/delete |
| `useCredentials()` | `["model-playground", "credentials"]` | credential create/replace/delete |
| `useCredentialMutations()` | — | invalidates both keys above on success |
| `useRuns(limit, offset)` | `["model-playground", "runs", limit, offset]` | run create/delete |
| `useRun(id)` | `["model-playground", "run", id]` | — (immutable once created; not invalidated by other runs) |
| `useRunMutations()` | — | invalidates `["model-playground", "runs"]` on create/delete; removes `["model-playground", "run", id]` on delete |

This follows the same invalidate-list-on-mutation / `setQueryData`-on-create pattern already used in `features/prompt-studio/api.ts`.

## 5. TODO

- [ ] Assign a phase owner.

## 6. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
