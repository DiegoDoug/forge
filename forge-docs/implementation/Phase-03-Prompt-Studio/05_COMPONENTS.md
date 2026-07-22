# Prompt Studio — Components

> **Purpose:** Frontend component inventory for this phase — what gets built, and what's reused from the existing design system.
> **Scope:** Component-level detail. Screen-level UX lives in 02_UI.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved alongside [`02_UI.md`](02_UI.md) 2026-07-22.
> **Last Updated:** 2026-07-22

---

## 1. New components

| Component | Responsibility |
|---|---|
| `PromptList` | Renders the searchable, tag-filterable list of prompt cards (§1.1 in `02_UI.md`); owns the search/tag-filter local state. |
| `PromptListItem` | One prompt card: name, description excerpt, tags, version badge, last-updated. |
| `PromptEditor` | The right-pane container: composes metadata row, `VariablesPanel`, `PromptBodyEditor`, `PreviewPanel`; owns dirty-state tracking for Save/Discard. |
| `PromptMetadataRow` | Inline-editable name/description/tags + the Duplicate/History/Delete toolbar. |
| `VariablesPanel` | List of variable rows with add/edit/remove; validates `name` pattern/uniqueness client-side before it ever reaches the API. |
| `VariableRow` | One variable's name/type/required/default/description fields. |
| `PromptBodyEditor` | Wraps `@monaco-editor/react` in plain-text mode; highlights `${declaredName}` vs. unknown `${...}` tokens using the same extraction rule as the backend's `templating.py` (reimplemented in TS — see §4). |
| `PreviewPanel` | Renders one input per declared variable and the live-substituted output; implements the shared substitution algorithm client-side; owns the Copy action. |
| `VersionHistoryPanel` | Slide-over listing versions; hosts version selection (single → detail, two → diff) and the Restore action with confirmation. |
| `VersionDiffView` | Wraps the existing `diff`-package-based diff rendering (same approach as the Converters diff viewer) for two version bodies. |
| `NewPromptDialog` / inline empty-detail state | Entry point for creating a prompt when none is selected. |
| `DeletePromptDialog`, `RestoreVersionDialog` | Confirmation dialogs for the two destructive/state-changing actions in this phase, per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2. |

## 2. Reused components

- shadcn/ui primitives: `Dialog` (confirmations), `Input`/`Textarea` (metadata, variable fields), `Badge` (tags, version number), `Command`/`Popover` (tag filter, if a combobox pattern is used), `Sonner` toast (save/error feedback), `Skeleton` (loading states).
- `frontend/components/app-shell/` — no changes; the new page slots into the existing shell via the nav-registry entry, same as every other feature.
- `@monaco-editor/react` — already a dependency; no new editor is introduced.
- The existing diff-rendering component backing the Converters diff viewer (reused, not duplicated, for `VersionDiffView` — exact import path to confirm during implementation by reading `frontend/features/converters/` for its diff viewer's component, per the playbook's "check for prior art" step).

## 3. `features/` structure

```
frontend/features/prompt-studio/
  api.ts                     # the only file that knows /api/prompts/* shapes
  types.ts                   # PromptVariable, Prompt, PromptVersion TS types (mirrors schemas/prompt_studio.py)
  templating.ts              # extractPlaceholders(body), substitute(body, values) — TS mirror of backend/app/services/prompt_studio/templating.py (see 03_BACKEND.md §2.1)
  prompt-list.tsx
  prompt-list-item.tsx
  prompt-editor.tsx
  prompt-metadata-row.tsx
  variables-panel.tsx
  variable-row.tsx
  prompt-body-editor.tsx
  preview-panel.tsx
  version-history-panel.tsx
  version-diff-view.tsx
  new-prompt-dialog.tsx
  delete-prompt-dialog.tsx
  restore-version-dialog.tsx
frontend/app/(app)/prompt-studio/
  page.tsx                   # composes PromptList + PromptEditor, reads/writes ?id= for deep-linking
```

`api.ts` is the only file aware of `/api/prompts/*` endpoint shapes, per [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1 — every component above consumes the TanStack Query hooks it exports (§4), never an ad hoc `fetch`.

## 4. State management

TanStack Query hooks exported from `api.ts`, cache key namespaced under `["prompt-studio", ...]` (matching Project Init's `["project-init", ...]` convention):

| Hook | Query key | Invalidates on |
|---|---|---|
| `usePrompts(search?, tag?)` | `["prompt-studio", "list", search, tag]` | create, delete, duplicate, metadata update, content update (name/tags shown in the list can change) |
| `usePrompt(id)` | `["prompt-studio", "detail", id]` | metadata update, content update, restore (for that `id`) |
| `usePromptVersions(id)` | `["prompt-studio", "versions", id]` | content update, restore (for that `id`) — a new version appears |
| `usePromptVersion(id, versionId)` | `["prompt-studio", "version", id, versionId]` | never (a specific version's content is immutable once created) |
| `useCreatePrompt()` | mutation | invalidates `["prompt-studio", "list"]` |
| `useUpdatePromptMetadata(id)` | mutation | invalidates `["prompt-studio", "list"]`, `["prompt-studio", "detail", id]` |
| `useUpdatePromptContent(id)` | mutation | invalidates `["prompt-studio", "detail", id]`, `["prompt-studio", "versions", id]`, `["prompt-studio", "list"]` |
| `useDeletePrompt()` | mutation | invalidates `["prompt-studio", "list"]` |
| `useDuplicatePrompt(id)` | mutation | invalidates `["prompt-studio", "list"]` |
| `useRestoreVersion(id)` | mutation | invalidates `["prompt-studio", "detail", id]`, `["prompt-studio", "versions", id]`, `["prompt-studio", "list"]` |

The Preview panel's live substitution (§1's `PreviewPanel`) is **not** a TanStack Query hook — it's local component state recomputed synchronously via `templating.ts` on every keystroke, per [`01_SPEC.md`](01_SPEC.md) §3.5's "never leaves the browser" requirement.

## 5. TODO

- [ ] None — this document is filled in for the specification review pass.

## 6. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
