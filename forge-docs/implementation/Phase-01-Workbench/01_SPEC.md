# Workbench — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; the panel contract lives in 12_PANEL_INTERFACE.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — third full pass (scope frozen, compatibility-migration refinements), pending final confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../../00_VISION.md](../../00_VISION.md), [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md), [../../decisions/0001-workbench-replaces-dashboard.md](../../decisions/0001-workbench-replaces-dashboard.md) through [0007-search-dedicated-page.md](../../decisions/0007-search-dedicated-page.md)
> **Supersedes:** v0.2.0 of this document (Secrets rename as a flat rename rather than a compatibility migration; open scope questions not yet resolved)

---

## 1. Summary

Give Forge a configurable home workspace — the **Workbench** — that surfaces pinned tools, recent activity across every feature, and quick actions. Workbench fully replaces the Dashboard concept ([ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md)): there is no "Dashboard" anywhere in the app or docs going forward, only Workbench, at the same route (`/`), sidebar position, and shortcut (`D`) Dashboard held.

Workbench does not know what its contents are. It is a runtime that lays out, persists, and renders **panels** — any component implementing the `WorkbenchPanel` interface ([`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md)) and registered with the panel registry ([ADR-0002](../../decisions/0002-workbench-panel-architecture.md)). This is a deliberate departure from a fixed, hardcoded "widget" catalog: adding Workbench presence for a future phase (Prompt Studio, Model Playground, Projects, Knowledge Hub) means that phase registers a panel — it never means editing Workbench's own code.

## 2. User stories

- As a developer who uses Forge daily, I want to pin the tools I reach for most (e.g. Secrets, Notes, Ingest) so they're one click away from my home screen instead of scanning the full sidebar every time.
- As a developer, I want to see recent activity across every feature on my home screen, exactly as Dashboard showed it, so I can jump back into what I was doing.
- As a developer, I want quick actions (new note, new secret, generate a password) available directly from my home screen so I don't have to navigate into a feature first just to start one.
- As a developer, I want the storage/system status I see today (disk usage, database size, version) to remain visible, so nothing I already rely on regresses.
- As a developer, I want to hide panels I don't care about and reorder the ones I keep, so my home screen matches how I actually work rather than a fixed factory layout.
- As a developer, I want my layout to persist across browser sessions and devices on my LAN, so I don't have to re-customize it every time I open Forge from a different machine.
- As a developer opening Forge for the first time, I want a sensible, fully-populated default layout, so Workbench isn't an empty page before I've customized anything.
- As a developer, I want a one-click way to undo my customization and return to the default layout, so experimenting with the layout is never a one-way door.
- As a developer, I want a real search page I can pin and jump to, not just the command palette, so I can see all my matches at once when a quick ⌘K glance isn't enough.
- As someone building a future Forge phase, I want to add my feature's presence to Workbench by writing a component and registering it — no pull request touching Workbench's own code — so my phase's timeline is never blocked on Workbench's.

## 3. Functional requirements

1. The app's home route (`/`) renders the Workbench: a grid of panels, replacing the former fixed Dashboard layout. The route does not change.
2. Workbench renders any panel that is both **registered** (per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §4) and marked **visible** in the persisted layout. There is no fixed enum of allowed panel types inside Workbench's own code.
3. Phase 01 ships five **active** panels: **Pinned Tools**, **Recent Activity**, **Quick Actions**, **Storage & System**, **Recent Notes**. A sixth panel type, **Recent Projects**, is defined in the catalog and interface now but ships unregistered/inactive — it renders nothing until Phase 06 (Projects) implements the real data and registers it ([ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md)). The former **Recent Secrets** panel is removed outright, not merely hidden by default (see §5).
4. Each registered panel can independently be shown or hidden.
5. Visible panels can be reordered; the order persists.
6. A user can pin or unpin any entry from the app's full navigation catalog (`frontend/lib/nav-registry.ts`, plus the forward-looking entries in requirement 8 below) to the Pinned Tools panel. Pinned tools display in a user-defined order.
7. The full layout — panel visibility, panel order, and the pinned-tools list and order — persists server-side, instance-wide ([ADR-0003](../../decisions/0003-workbench-single-row-layout.md); this is a single-tenant app, [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.1 — there is no per-user or per-device layout). It survives reload, logout/unlock, and access from a different browser on the same instance.
8. A "Reset to default layout" action restores the shipped default panel set, order, and pinned-tools list in one step.
9. Before any customization has been saved, Workbench renders the shipped default layout:
   - Panels: Pinned Tools, Recent Activity, Quick Actions, Storage & System, Recent Notes — all visible, in that order.
   - Pinned tools (6, the approved default): **Ingest**, **Notes**, **Prompt Studio**, **Universal Converter**, **Secrets**, **Search**. Prompt Studio and Universal Converter are not yet implemented (Phases 03 and 04) — their pins render as disabled "coming soon" tiles (linking nowhere, per §6) rather than being omitted, per the project owner's explicit direction. Secrets and Search depend on requirements 12 and 13 below.
10. The **Recent Activity**, **Storage & System**, and **Recent Notes** panels show exactly the data the former Dashboard showed for their equivalents (same counts, same fields) — this phase re-homes that data into panels, it does not change what it contains.
11. The **Quick Actions** panel surfaces at minimum: "New note," "New secret," and "Generate password" as one-click shortcuts that deep-link into the relevant feature's creation flow.
12. Workbench remains reachable from the sidebar and the command palette exactly as Dashboard was, now labeled "Workbench" (per [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md)).
13. **Secrets rename dependency:** the "Secrets" pinned-tool entry in requirement 9 depends on the Vault → Secrets rename having landed **as a compatibility migration** ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)) — UI, routes, components, services, and API endpoints rename to Secrets, with the old `/vault` route and `/api/vault` endpoint kept as working aliases (not hard-removed), and the database table renamed only if that's safe without a risky data migration. This is tracked as a prerequisite implementation task (see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)), not something this spec silently assumes is already true in the shipped code.
14. **Search page dependency:** the "Search" pinned-tool entry in requirement 9 depends on a new dedicated `/search` page existing ([ADR-0007](../../decisions/0007-search-dedicated-page.md)), reusing the existing `GET /api/search` endpoint — no backend change, but a real new frontend route delivered as part of this phase.
15. **Extensibility:** a developer can add a new panel to Workbench by (a) writing a component implementing `WorkbenchPanelProps`, (b) calling `registerWorkbenchPanel(...)` with its metadata, and (c) importing that registration module from the bootstrap list (per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §4) — with no change to any file inside `frontend/features/workbench/` itself beyond the bootstrap import list.

## 4. Relationship to existing features

Evolves and fully replaces the former **Dashboard** feature (`frontend/features/dashboard/`, `backend/app/services/dashboard.py`, `backend/app/api/routes/dashboard.py`) — see [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md). Also depends on, but does not itself implement: the Vault → Secrets rename ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)) and a new Search page ([ADR-0007](../../decisions/0007-search-dedicated-page.md)), both scoped as Phase 01 prerequisite/companion tasks because the approved default pinned-tools list depends on them existing. No other shipped feature's data model changes.

## 5. Explicitly out of scope

- **Per-user or per-device layouts.** Forge is single-tenant by design ([`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.1); the layout is one instance-wide configuration.
- **A general-purpose, user-facing panel builder.** The panel interface ([`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md)) is a developer-facing extension point (register a component in code), not an end-user "build your own widget" feature.
- **Implementing Prompt Studio, Universal Converter, Model Playground, Knowledge Hub, or Projects themselves.** Those remain Phases 03–07. This phase only adds placeholder/disabled pin entries for Prompt Studio and Universal Converter (requirement 9) and a defined-but-inactive Recent Projects panel type (requirement 3).
- **Recent Secrets, in any form.** Removed outright per the project owner's decision — more useful, less sensitive alternatives (Recent Projects, once Phase 06 lands) take its place in the catalog. There is no "hidden by default but still available" fallback for it.
- **Changes to global search's backend behavior.** [ADR-0007](../../decisions/0007-search-dedicated-page.md) adds a frontend route reusing the existing `GET /api/search` endpoint unchanged.
- **A dedicated mobile-only redesign.** Workbench must meet the same responsive/accessibility bar as every other feature ([`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §3–4).
- **Deleting the underlying data models Workbench's panels read from.** `ActivityLog` and `Note` are reused as-is (see [`04_DATABASE.md`](04_DATABASE.md)).
- **Workflows, in any form.** Explicitly excluded by project-owner decision: Phase 01 delivers Workbench, its panels, the layout system, and the Panel Registry — nothing else. Workflow nodes, if they ever exist, are a later phase's concern.
- **A generalized Capability Registry.** [ADR-0008](../../decisions/0008-capability-registry-direction.md) records this direction but is `Proposed`, not `Accepted` — Phase 01 builds the narrower Panel Registry from [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) only. Do not generalize the registry as part of this phase's implementation.
- **A Projects interface (`ProjectProvider`/`ProjectContext`/`CurrentProject`/`NoProject`).** [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) stands as accepted: Projects-related code, including a context/provider shell, is Phase 06's deliverable, not Phase 01's. Workbench does not run in a "Global Mode vs. Project Mode" distinction this phase — there is only one mode, because Projects don't exist yet.
- **The command palette becoming a full action/command surface.** [ADR-0007](../../decisions/0007-search-dedicated-page.md) §6 records this as a future direction; Phase 01 ships only the `/search` results page.

## 6. Resolved questions (formerly open)

All scope questions raised across the previous two drafts have been resolved by the project owner as of 2026-07-20:

- **Disabled pin representation** — resolved: the backend tool catalog (`03_BACKEND.md` §3) carries an `available` flag per tool key, echoed in `WorkbenchLayoutOut` (`06_API.md` §2), so the frontend never needs a second hardcoded "coming soon" list.
- **Sequencing of the Secrets rename and Search page** — resolved: both are the first entries in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md), ahead of panel/layout work that depends on them; the Secrets rename ships as a compatibility migration per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md), not a breaking cutover.
- **Recent Projects panel's registration trigger** — resolved: Phase 06 registers it as part of its own `IMPLEMENT.md`; Phase 01 defines the `type` and interface accommodation only (per [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md)) and does not implement it.
- **Capability Registry generalization and a Projects interface** — resolved: both deferred, per [ADR-0008](../../decisions/0008-capability-registry-direction.md) (Proposed) and [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) (Accepted, unchanged) respectively — see §5's scope-freeze bullets above.
- **Command palette scope** — resolved: Phase 01 ships the `/search` page only; the full command-surface direction is recorded in [ADR-0007](../../decisions/0007-search-dedicated-page.md) §6 and explicitly deferred.

No open questions remain blocking this spec. Remaining work before `IMPLEMENT.md` is authorized is project-owner sign-off on the drafted documents themselves (see [`README.md`](README.md) "Exit Criteria"), not further scope decisions.

## 7. TODO

- [ ] TODO: Get final project-owner sign-off recorded against [`README.md`](README.md) "Exit Criteria" before `IMPLEMENT.md` is authorized for this phase.

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [../../decisions/0001-workbench-replaces-dashboard.md](../../decisions/0001-workbench-replaces-dashboard.md) through [0008-capability-registry-direction.md](../../decisions/0008-capability-registry-direction.md)
- [../../00_VISION.md](../../00_VISION.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
