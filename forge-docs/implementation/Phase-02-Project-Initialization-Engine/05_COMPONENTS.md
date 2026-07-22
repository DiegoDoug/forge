# Project Initialization Engine — Components

> **Purpose:** Frontend component breakdown for this phase.
> **Scope:** Component structure and props only. Screen-level UX lives in 02_UI.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted.
> **Last Updated:** 2026-07-22

---

## 1. Component tree

```
app/(app)/project-init/page.tsx
└── features/project-init/
    ├── api.ts                        typed fetch + React Query hooks (useCatalog, useHistory, useGenerate, useDeleteGeneration)
    ├── kind-picker.tsx                the two selectable kind cards (§1 of 02_UI.md)
    ├── fdk-phase-form.tsx             phase_number / phase_name / objective, plain-state validated
    ├── ai-instructions-form.tsx       project_name / description / tech_stack (tag input) / conventions / output_files checklist
    ├── file-preview.tsx               read-only Accordion listing the filenames the current form state will produce
    ├── generation-history.tsx         history list + delete confirmation dialog
    └── generation-actions.ts          shared "generate then trigger browser download" helper used by both forms
```

## 2. Component responsibilities

- **`kind-picker.tsx`** — pure UI state (`selectedKind: "fdk_phase" | "ai_instructions" | null`), lifted to `page.tsx`. Renders the fixed catalog fetched via `useCatalog()` (labels/descriptions come from the backend catalog, not hardcoded, so the frontend never drifts from `03_BACKEND.md`'s `catalog.py`).
- **`fdk-phase-form.tsx` / `ai-instructions-form.tsx`** — plain `useState` per field with inline validation functions mirroring the backend field constraints in [06_API.md §1](06_API.md) exactly (max lengths, required-ness, `output_files` min-items-1) — matching every existing Forge tool form's pattern (`features/generators/password-generator.tsx` et al.), not `react-hook-form`/`zod` (listed in the tech stack but unused by any shipped feature; not worth introducing a new shadcn `Form` primitive for three simple fields). On submit, calls `generation-actions.ts`'s shared helper rather than each form owning its own fetch/download logic.
- **`file-preview.tsx`** — for the "Preview files" disclosure ([02_UI.md](02_UI.md) §1). Lists the filenames the current kind will produce (from the catalog's `output_files`, or the selected `output_files` checklist for ai_instructions) with a static description of each file's purpose — not a byte-for-byte rendered preview. An exact client-rendered preview would require duplicating `renderer.py`'s template logic in TypeScript, a maintenance-cost duplication this phase avoids; deferred as a nice-to-have, not required by [01_SPEC.md](01_SPEC.md).
- **`generation-actions.ts`** — `async function generateAndDownload(kind, config)`: calls `POST /generate` (via `api.ts`), then `GET /{id}/download`, converts the response to a `Blob`, and triggers a synthetic `<a download>` click — consistent with the existing Documents export button's client-side download pattern (`features/documents`) rather than inventing a second mechanism.
- **`generation-history.tsx`** — consumes `useHistory()`; each row's "Download" button re-runs the download half of `generation-actions.ts` against the existing `id` (no re-generate call); "Delete" opens the shared `components/ui/dialog.tsx` confirmation before calling `useDeleteGeneration()`.
- **`page.tsx`** — composes `page-header.tsx`, `kind-picker.tsx`, the active form, `file-preview.tsx`, and `generation-history.tsx`; owns `selectedKind` state; renders the §3 empty/loading/error states from [02_UI.md](02_UI.md).

## 3. `features/project-init/` structure

`api.ts` is the only file in this feature aware of backend endpoint shapes, per [`../../07_CODING_STANDARDS.md §1`](../../07_CODING_STANDARDS.md). All other files above consume its exported hooks/types only.

## 4. State management

TanStack Query hooks, all in `features/project-init/api.ts`:

- `useCatalog()` — `queryKey: ["project-init", "catalog"]`, effectively static (long `staleTime`, e.g. `Infinity` — the catalog only changes on a backend deploy).
- `useHistory(limit = 20)` — `queryKey: ["project-init", "history", limit]`.
- `useGenerate()` — mutation; `onSuccess` invalidates `["project-init", "history"]`.
- `useDeleteGeneration()` — mutation; `onSuccess` invalidates `["project-init", "history"]`.

## 5. Reused components

`components/page-header.tsx`, `components/empty-state.tsx`, `components/tool-card.tsx`, `components/ui/skeleton.tsx`, `components/ui/dialog.tsx`, `components/ui/accordion.tsx`, `components/ui/alert.tsx`, `components/ui/badge.tsx` (kind tag in history rows), `components/ui/button.tsx`, `components/ui/input.tsx`, `components/ui/textarea.tsx`, `components/ui/checkbox.tsx`, `components/ui/label.tsx`. No new shared component is introduced — everything this phase needs already exists in `components/ui/`.

## 6. TODO

None.

## 7. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
