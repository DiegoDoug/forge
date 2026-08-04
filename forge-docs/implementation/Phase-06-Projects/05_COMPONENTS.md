# Projects — Components

> **Purpose:** Frontend component inventory for this phase — what gets built, and what's reused from the existing design system.
> **Scope:** Component-level detail. Screen-level UX lives in 02_UI.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Confirmed
> **Last Updated:** 2026-08-02

---

## 1. New components

`frontend/features/projects/`:

- `project-card.tsx` — one project's summary in the list grid (name, color, counts, archived badge).
- `project-form-dialog.tsx` — create/edit dialog (name, description, color).
- `project-delete-dialog.tsx` — delete confirmation, explicit "children are unassigned, not deleted" copy.
- `project-picker.tsx` — reusable `<Select>` project picker, consumed by Secrets/Notes/Documents forms and list filters.
- `project-ai-config.tsx` — default provider/model picker + configured-status badge.
- `project-ai-quick-run.tsx` — prompt box + submit + inline result.
- `workbench-panel.tsx` — registers the `recent_projects` Workbench panel.

New pages: `frontend/app/(app)/projects/page.tsx`, `frontend/app/(app)/projects/[id]/page.tsx`.

## 2. Reused components

- `components/page-header.tsx`, `components/empty-state.tsx`, `components/ui/skeleton.tsx` — same list/detail scaffolding every other feature page uses.
- `components/ui/dialog.tsx`, `components/ui/select.tsx`, `components/ui/textarea.tsx`, `components/ui/button.tsx`, `components/ui/badge.tsx` — shadcn primitives, no new ones needed.
- `features/model-playground/result-panel.tsx`'s result-rendering (imported for the quick-run result, not reimplemented).
- `features/model-playground/api.ts`'s `useProviders()` hook (read-only reuse for the AI config picker's provider/model catalogue).
- `features/workbench/panel-registry.ts`'s `registerWorkbenchPanel` (same registration call every panel-owning feature makes).

## 3. `features/` structure

- `frontend/features/projects/api.ts` — the only file that knows this phase's `/api/projects` endpoint shapes (per `../../07_CODING_STANDARDS.md` §1): `projectsApi` object + `useProjects`, `useProject`, `useProjectMutations`, `useProjectAiRuns`, `useProjectAiRun`.
- Component files as listed in §1 above, each a focused, single-responsibility file matching the granularity of `features/model-playground/*.tsx`.

## 4. State management

TanStack Query, same conventions as `features/model-playground/api.ts`:

- `["projects", { archived }]` — list query.
- `["projects", "project", id]` — detail query.
- `["projects", "project", id, "ai-runs"]` — project-scoped AI run history.
- Mutations (create/update/delete/run-ai) invalidate `["projects"]` broadly on list-affecting changes and `["projects", "project", id]` on detail-affecting changes, mirroring `useCredentialMutations`'s dual-invalidate pattern.
- Cross-feature invalidation: assigning/reassigning a secret/note/document's `project_id` (via each feature's own mutation) additionally invalidates `["projects"]` so list counts stay fresh — a small addition to `useSecretMutations`/`useNoteMutations`/`useDocumentMutations`' existing `onSuccess` handlers, not a new cross-feature subscription mechanism.

## 5. TODO

None — this document is confirmed, not a template placeholder.

## 6. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
