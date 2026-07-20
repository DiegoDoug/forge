# Workbench — Panel Interface

> **Purpose:** The `WorkbenchPanel` contract — the one thing every piece of Workbench content implements, so the Workbench runtime never needs to know what a panel is for.
> **Scope:** The interface, registration, and lifecycle only. Specific panel implementations (Pinned Tools, Recent Activity, etc.) live in [`05_COMPONENTS.md`](05_COMPONENTS.md); the host runtime that renders panels lives in [`05_COMPONENTS.md`](05_COMPONENTS.md) (`WorkbenchGrid`) and [`03_BACKEND.md`](03_BACKEND.md) (layout persistence).
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — first full pass, pending confirmation
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_SPEC.md](01_SPEC.md), [../../decisions/0002-workbench-panel-architecture.md](../../decisions/0002-workbench-panel-architecture.md)
> **Supersedes:** —

---

## 1. Overview

A **panel** is a self-contained unit of Workbench content that implements `WorkbenchPanel` and registers itself with the panel registry. The Workbench runtime (`WorkbenchGrid`, per [`05_COMPONENTS.md`](05_COMPONENTS.md)) hosts panels generically: it knows how to lay out, show/hide, reorder, and persist state for anything conforming to this contract — it has zero knowledge of what any specific panel does or renders. This is the mechanism behind [ADR-0002](../../decisions/0002-workbench-panel-architecture.md): a new panel is added by a feature registering itself, never by editing Workbench's own code.

## 2. The contract

```ts
// frontend/features/workbench/panel-types.ts

interface WorkbenchPanelDefinition {
  type: string;                              // stable, unique key — e.g. "pinned_tools"
  metadata: WorkbenchPanelMetadata;
  component: React.ComponentType<WorkbenchPanelProps>;
}

interface WorkbenchPanelMetadata {
  title: string;
  description: string;
  icon: LucideIcon;
  defaultVisible: boolean;
  minColumnSpan?: number;                    // responsive sizing hint, see §9
  permissions?: WorkbenchPanelPrecondition[]; // see §8
}

interface WorkbenchPanelProps {
  mode: "view" | "customize";
  onError: (error: unknown) => void;         // see §3
}
```

Each panel owns its own data fetching (its own TanStack Query hook, calling its own feature's `api.ts`) — the registry carries only metadata and a component reference, never data. This keeps `WorkbenchGrid` itself free of any panel-specific network calls.

## 3. Lifecycle

1. **Registration** — happens once, at module load, before first render (see §4). A panel's `type` becomes renderable the moment it's registered.
2. **Mount** — `WorkbenchGrid` renders a panel inside a shared `WorkbenchPanelCard` shell (per [`05_COMPONENTS.md`](05_COMPONENTS.md)) whenever the panel's `type` is both **registered** and marked **visible** in the current persisted layout.
3. **Own data fetch** — the panel component manages its own loading/error/populated state internally. `WorkbenchGrid` never fetches content on a panel's behalf.
4. **Error containment** — `WorkbenchPanelCard` wraps every panel in a React error boundary. A panel can also proactively call `onError` to present the shared "this panel failed" card state without crashing the rest of the grid — required so one panel's failure can never blank the page (per [`02_UI.md`](02_UI.md) §3.1).
5. **Hide/unmount** — a hidden panel is simply not rendered; it is not "unmounted with state preserved." Toggling it back visible remounts it fresh.
6. **Unregistered `type` in a saved layout** — the persisted layout may reference a `type` string with no matching registry entry (e.g. from a panel belonging to a not-yet-shipped phase, or a panel that's been removed). The runtime **silently skips rendering it** rather than erroring. This is the exact mechanism [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) relies on: a `recent_projects` entry can exist in the default layout's `panels` list today, render nothing (because no panel registers that `type` yet), and start rendering the moment Phase 06 registers it — with no Workbench code change.

## 4. Registration

- `frontend/features/workbench/panel-registry.ts` exports `registerWorkbenchPanel(definition)` and `getRegisteredPanels()`.
- Each panel-owning feature calls `registerWorkbenchPanel(...)` once, at import time, from its own feature folder — e.g. `frontend/features/notes/workbench-panel.tsx` registers the Recent Notes panel. **Workbench's own code never lists panels by name**, per [ADR-0002](../../decisions/0002-workbench-panel-architecture.md).
- A single bootstrap module (e.g. `frontend/features/workbench/register-all.ts`), imported once from the app shell, imports every panel-owning feature's registration module — so registration is guaranteed to happen exactly once, deterministically, regardless of what else has loaded.
- No dynamic/runtime plugin loading. Registration is a compile-time list of imports, per [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) §3 (the plugin-loading alternative was explicitly rejected as over-engineering for a single-deployment app).

## 5. Metadata

| Field | Required | Purpose |
|---|---|---|
| `title` | Yes | Display name in the panel card header and the customize-mode panel list. |
| `description` | Yes | One line, shown in the customize-mode panel list to explain what a hidden panel does. |
| `icon` | Yes | `lucide-react` icon, consistent with [`../../05_DESIGN_SYSTEM.md`](../../05_DESIGN_SYSTEM.md) §5. |
| `defaultVisible` | Yes | Whether this panel is on in the shipped default layout (per [`01_SPEC.md`](01_SPEC.md) §3, requirement 8). |
| `minColumnSpan` | No | Responsive sizing hint — see §9. |
| `permissions` | No | Preconditions for meaningful rendering — see §8. |

## 6. Actions

Panel-specific action affordances (e.g. Pinned Tools' "manage pinned tools" button, Quick Actions' buttons themselves) are owned and rendered by the panel component — they are not part of the generic host contract. The generic host chrome (`WorkbenchPanelCard`) contributes exactly two host-level controls, both customize-mode-only and identical for every panel: the visibility toggle and the drag handle. A panel component never needs to implement or opt into these — they wrap around whatever the panel renders.

## 7. Persistence

Panel visibility and order persist through the single-row `workbench_layout` table ([ADR-0003](../../decisions/0003-workbench-single-row-layout.md)), as `panels: list[{"type": str, "visible": bool}]` in display order.

**Backend implication:** the backend does not — and cannot — validate `type` against a fixed enum of known panels, because panel existence is a frontend build-time fact (which features were compiled into the bundle and registered), invisible to the backend. `03_BACKEND.md` §2 validates only structural shape on `PUT /api/workbench/layout` — each entry is a non-empty string `type` and a boolean `visible`, with no duplicate `type` values — and leaves "does this panel actually exist" entirely to the frontend registry lookup described in §3, item 6.

## 8. Permissions

Forge has no user roles or RBAC ([`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.1), so `permissions` here does not mean access control. It means: **preconditions for a panel to render something meaningful.** Example: a future Model Playground panel might declare a precondition of "at least one provider configured." If a declared precondition isn't met, the panel renders its **own** "not available yet" / "needs setup" state — it is not force-hidden by the host. This keeps the gap honest and visible rather than silently disappearing, consistent with [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.3.

## 9. Responsive behavior

- `minColumnSpan` lets a panel declare it needs more horizontal room than the grid's default column width (e.g. Recent Activity's list vs. Storage & System's compact stat block). `WorkbenchGrid`'s breakpoints (per [`05_COMPONENTS.md`](05_COMPONENTS.md)) respect this hint on desktop/tablet widths.
- Every panel must still degrade to full single-column width on mobile, per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §3 — `minColumnSpan` is a desktop layout hint only, never an excuse to skip mobile support.

## 10. Example: registering a panel

```tsx
// frontend/features/notes/workbench-panel.tsx
import { StickyNote } from "lucide-react";
import { registerWorkbenchPanel } from "@/features/workbench/panel-registry";
import { RecentNotesPanel } from "./components/RecentNotesPanel";

registerWorkbenchPanel({
  type: "recent_notes",
  metadata: {
    title: "Recent Notes",
    description: "Your most recently updated notes.",
    icon: StickyNote,
    defaultVisible: true,
  },
  component: RecentNotesPanel,
});
```

`RecentNotesPanel` itself owns its `useQuery` call against `frontend/features/notes/api.ts` — Workbench never sees that request.

## 11. TODO

- [ ] TODO: Confirm the error-boundary implementation approach (React's built-in `componentDidCatch` class boundary vs. a library like `react-error-boundary`) once [`06_TECH_STACK.md`](../../06_TECH_STACK.md) is checked for an existing dependency.
- [ ] TODO: Decide whether panels need an imperative `refresh()` method exposed to the host (e.g. for a manual refresh action) — deferred as not needed by any Phase 01 panel; revisit if a future panel (e.g. Model Playground) needs it.
- [ ] TODO: This document is a first full pass — confirm before `IMPLEMENT.md` is authorized, per the exit criteria in [`README.md`](README.md).

## 12. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../decisions/0002-workbench-panel-architecture.md](../../decisions/0002-workbench-panel-architecture.md)
- [../../decisions/0005-projects-primary-organizational-unit.md](../../decisions/0005-projects-primary-organizational-unit.md)
