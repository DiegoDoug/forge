# Workbench — Components

> **Purpose:** Frontend component inventory for this phase — what gets built, and what's reused from the existing design system.
> **Scope:** Component-level detail. Screen-level UX lives in 02_UI.md; the panel contract itself lives in 12_PANEL_INTERFACE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — second full pass (panel architecture), pending confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [02_UI.md](02_UI.md), [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md), [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md), [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
> **Supersedes:** v0.2.0 of this document (Secrets feature-folder rename framed without the alias/compatibility nuance)

---

## 1. New components

### 1.1 Workbench runtime (generic — no panel-specific knowledge)

| Component | Responsibility |
|---|---|
| `WorkbenchGrid` | Renders the responsive grid/stack of visible, *registered* panels in saved order; owns the customize-mode on/off state; iterates `getRegisteredPanels()` (per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §4) — never imports a specific panel component. |
| `WorkbenchPanelCard` | Shared card shell every panel renders inside — title/icon from panel metadata, drag handle (customize mode only), visibility toggle (customize mode only), and a per-panel React error boundary (per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §3). Renamed from the earlier `WorkbenchWidgetCard`. |
| `WorkbenchCustomizeToggle` | Header control that enters/exits customize mode; also exposed as a command-palette action. |
| `WorkbenchEmptyState` | Rendered by `WorkbenchGrid` when every registered panel is hidden. |
| `WorkbenchResetButton` | Triggers reset-to-default with the confirmation step required by [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2. |
| `PinPickerDialog` | Dialog listing every `NAV_ITEMS` entry plus the forward-looking `prompt_studio`/`universal_converter` entries (from `WorkbenchLayoutOut`'s tool catalog echo, per [`06_API.md`](06_API.md) §2), each with a pin/unpin toggle. Renders disabled entries with a "Coming soon" badge. |

### 1.2 Panels (each implements `WorkbenchPanel`, per 12_PANEL_INTERFACE.md)

| Component | Panel `type` | Responsibility |
|---|---|---|
| `PinnedToolsPanel` | `pinned_tools` | Renders pinned tools as clickable tiles; disabled tiles for not-yet-available tools render inert (no click target, "Coming soon" label); "Manage" action opens `PinPickerDialog`. |
| `RecentActivityPanel` | `recent_activity` | Renders the recent-activity list, same content as the former Dashboard. |
| `QuickActionsPanel` | `quick_actions` | Static set of one-click action buttons (new note, new secret, generate password). |
| `SystemStatusPanel` | `system_status` | Renders storage/database/version stats — direct port of the former Dashboard's storage block. |
| `RecentNotesPanel` | `recent_notes` | Renders recent notes list — direct port of former Dashboard behavior. |

**Not built in this phase:** a `RecentProjectsPanel` (`type: "recent_projects"`) is *not* implemented here — per [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md), it is Phase 06's deliverable. Nothing in this phase's component list references it; its absence from the registry is exactly what makes it safely inert (per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §3, item 6).

**Also not a panel:** the former Recent Secrets widget has no successor component — it is removed, full stop (per [`01_SPEC.md`](01_SPEC.md) §3, requirement 3).

### 1.3 Search page (new, per ADR-0007)

| Component | Responsibility |
|---|---|
| `SearchPage` (`frontend/app/(app)/search/page.tsx`) | Full-page search UI: input + results, reusing `frontend/features/search/api.ts` (already exists). |
| `SearchResultList` | Renders the same secrets/notes/documents match groups the command palette already renders, at full-page scale rather than palette-truncated. |

## 2. Reused components

- shadcn/ui `Card`, `Dialog`, `Switch`, `Button`, `Skeleton`, `AlertDialog` (for the reset confirmation) — all already in `frontend/components/ui/`, no new primitives added.
- `@dnd-kit/core`, `/sortable`, `/modifiers` — same libraries and drag-handle/keyboard-reorder pattern already proven by the Notes board.
- `sonner` toasts — for pin/unpin and layout-save failure feedback.
- `frontend/lib/nav-registry.ts`'s `NAV_ITEMS` — read directly rather than duplicated, for the *available* tools; forward-looking entries come from the backend's tool-catalog echo (see [`06_API.md`](06_API.md) §2), not a second hardcoded frontend list.
- `frontend/features/search/api.ts` — reused unchanged by the new `SearchPage`.

## 3. `features/` structure

- `frontend/features/workbench/api.ts` — the only file that knows the `/api/workbench` endpoint shapes (per [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1). Replaces `frontend/features/dashboard/api.ts`.
- `frontend/features/workbench/panel-registry.ts` — `registerWorkbenchPanel()` / `getRegisteredPanels()`, per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §4.
- `frontend/features/workbench/register-all.ts` — the single bootstrap import list, imported once from the app shell.
- `frontend/features/workbench/components/` — houses the runtime components in §1.1.
- Each panel's component lives inside its **owning** feature, not inside `features/workbench/` — e.g. `frontend/features/notes/workbench-panel.tsx` for `RecentNotesPanel`. `PinnedToolsPanel`, `QuickActionsPanel`, and `SystemStatusPanel` are the exceptions — they don't belong to any single existing feature, so they live in `features/workbench/components/`.
- `frontend/features/vault/` renames to `frontend/features/secrets/` as part of the compatibility migration ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)) — this is not itself a Workbench component, but Workbench's Quick Actions ("new secret") and Pinned Tools panels both reference it, so the rename must land before those panels can be considered done.
- `frontend/features/dashboard/` is removed once the cutover in `03_BACKEND.md` §1 is confirmed.

## 4. State management

- `useWorkbenchQuery()` — wraps `GET /api/workbench`; single cache key `["workbench"]`.
- `useUpdateLayoutMutation()` — wraps `PUT /api/workbench/layout`; optimistically updates the `["workbench"]` cache entry, rolling back on error with a toast.
- `useResetLayoutMutation()` — wraps `POST /api/workbench/layout/reset`; invalidates `["workbench"]` on success.
- Each panel manages its own query independently (e.g. `RecentNotesPanel` calls the existing Notes feature's own hooks) — Workbench's cache keys never expand to cover panel content, per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §2.

## 5. TODO

- [ ] TODO: Confirm the exact grid breakpoints/column counts referenced as an open item in [`02_UI.md`](02_UI.md) §6.
- [ ] TODO: Decide the exact `SearchPage` route/component split once [`06_API.md`](06_API.md)'s search-related section (if any) is confirmed — likely no changes needed there since it reuses the existing endpoint.

## 6. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
