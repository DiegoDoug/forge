# Workbench — Release Notes

> **Purpose:** The release-facing summary of Phase 01 — what shipped, what broke on purpose, what to do before upgrading. Not a duplicate of `CURRENT_STATE.md` (the day-to-day working log) or `POST_IMPLEMENTATION_REVIEW.md` (the retrospective) — this is the document a user or another engineer reads to understand what changed.
> **Scope:** This phase only.
> **Status:** Final — released as `v0.1.0-workbench`, tagged and merged to `master`, Phase 01 now frozen.
> **Version:** v0.1.0-workbench
> **Last Updated:** 2026-07-21
> **Depends On:** [../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../implementation/Phase-01-Workbench/CURRENT_STATE.md), [../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md](../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md), [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)

---

## New Features

- **Workbench** — a configurable home screen replacing the old fixed Dashboard, at the same route (`/`), sidebar position, and `D` shortcut. Ships with five panels: Pinned Tools, Recent Activity, Quick Actions, Storage & System, and Recent Notes.
- **Panel customization** — a "Customize" mode to show/hide panels, reorder them (mouse drag or full keyboard-only drag via arrow keys), and a one-click "Reset to default layout" with a confirmation step. All of it persists server-side, instance-wide, and survives reload/logout/a different browser.
- **Pinned tools** — pin or unpin any tool from the sidebar (plus the not-yet-built Prompt Studio and Universal Converter, shown as disabled "coming soon" tiles) via a dedicated pin-picker dialog, with a user-defined pin order.
- **Panel extensibility** — a `WorkbenchPanel` interface and registry so a future phase adds its own Workbench presence by writing a component and registering it, with zero changes to Workbench's own code. Demonstrated concretely by `RecentNotesPanel`, which lives in and is owned by the Notes feature, not Workbench.
- **Dedicated `/search` page** — a full-page search UI (secrets/notes/documents), reusing the existing `GET /api/search` endpoint unchanged, reachable from the Pinned Tools panel and the command palette.
- **Secrets** (renamed from Vault) — same feature, new name, with the old `/vault` route and `/api/vault` endpoint still working as compatibility aliases.

## Breaking Changes

- **The Dashboard is gone.** `/api/dashboard`, `backend/app/services/dashboard.py`, `backend/app/api/routes/dashboard.py`, and `frontend/features/dashboard/` are all deleted outright — a direct cutover, not a deprecation window (unlike the Vault→Secrets rename below). Anything that was calling `GET /api/dashboard` directly will get a 404.
- **Recent Secrets is removed, full stop** — not hidden, not optional. The former Dashboard's "recent secrets" widget has no successor; this was a deliberate product decision (fewer sensitive values surfaced by default), not an oversight.

## Migrations

- `0003_workbench_layout` (Alembic) — adds the `workbench_layout` table (single instance-wide row, `id=1`). No data migration: the row is created lazily on first access with the shipped default layout.
- No other schema changes. The Vault→Secrets rename did **not** require a table rename — `secrets`/`folders`/`tags`/`secret_versions`/`secret_tag_links` were already correctly named before the rename.

## Bug Fixes

- **`AlertDialogAction` never closed its dialog.** The shared `frontend/components/ui/alert-dialog.tsx` primitive's "Action" button ran its click handler but never closed the confirmation dialog, because Base UI (unlike Radix) has no auto-closing "Action" component — only "Close." This silently affected both the new Workbench "Reset to default" confirmation and the pre-existing Secrets "Delete" confirmation. Fixed by rebuilding `AlertDialogAction` on `AlertDialogPrimitive.Close`, matching how `AlertDialogCancel` was already correctly built. Re-verified end-to-end against both flows.
- **Panel drag-reorder / visibility-toggle data loss** ([`BUGS/BUG-0001`](BUGS/BUG-0001-panel-deletion-data-loss.md)). A panel `type` unrecognized by the running frontend build (e.g. a not-yet-shipped phase's panel) was silently and permanently deleted from a user's saved layout the moment they reordered or toggled any panel — found by a post-implementation code-review audit, not by functional testing. Fixed: the persistence path now preserves any such entry, untouched, in place.
- Panel registration bootstrap import moved from a Server Component (where it wasn't guaranteed to run in the browser bundle) to the Client Component that actually consumes the registry — found during T11's own browser verification.

## Known Issues

Tracked in [`BUGS/`](BUGS/README.md), all explicitly ruled non-blocking for this release by the project owner:

- 🟡 MAJOR — [`BUG-0003`](BUGS/BUG-0003-missing-error-toasts.md): 3 of 4 layout-mutating actions (panel reorder, panel visibility, pin reorder) show no error toast on failure — only the pin-picker's pin/unpin toggle does. The underlying rollback is always correct; only the user-facing failure message is missing.
- 🟢 MINOR — [`BUG-0002`](BUGS/BUG-0002-pinned-tools-duplicate-validation.md): the backend doesn't reject duplicate keys in a `pinned_tools` update (it does reject duplicate panel types). Not reachable through the shipped UI.
- 🟢 MINOR — [`BUG-0004`](BUGS/BUG-0004-dead-recent-notes-computation.md): the `/api/workbench` aggregate computes a `recent_notes` field that no panel actually reads (Recent Notes fetches its own data independently, correctly, per the panel architecture). Wasted, not wrong.
- 🟢 MINOR — [`BUG-0005`](BUGS/BUG-0005-unused-onerror-prop.md): the panel interface's optional `onError` escape hatch is never invoked by any of the five shipped panels — unexercised, not broken.
- Two accessibility issues in **global app-shell chrome that predates this phase** (not fixed here, since neither touches a file this phase owns): the mobile-nav hamburger button has no accessible name; the sidebar footer text and command-palette dialog header each trip a minor automated-scan finding.
- Temporary compatibility aliases from the Secrets rename (`/api/vault`, `/vault` → `/secrets` redirect) are known, tracked debt per ADR-0006 §4 — remove once nothing external depends on the old path.
- Two acceptance criteria are unverified, not failed: drag-reorder FPS/React Profiler re-render counts, and a live NVDA/VoiceOver/keyboard-only pass. Both require a real device/browser session; tracked as [`QA-0001`](QA/QA-0001-drag-performance.md) and [`QA-0002`](QA/QA-0002-screen-reader-audit.md).

## Upgrade Notes

- On first boot after this release, the home page changes from Dashboard to Workbench automatically — no user action required. The default layout (5 panels, 6 pinned tools) is created lazily on first access to `/api/workbench`.
- Anything bookmarked at `/vault` or calling `/api/vault` continues to work (compatibility alias). Anything that was calling `/api/dashboard` directly will need to switch to `/api/workbench`.
- No environment variables, config files, or manual migration steps are required beyond a normal deploy (the Alembic migration runs automatically on startup, same as every prior migration in this app).

## Deferred Work

- **Prompt Studio, Universal Converter, Model Playground, Knowledge Hub, Projects** — not implemented; Workbench ships placeholder "coming soon" pin entries and a defined-but-inactive `recent_projects` panel type for these, per `01_SPEC.md` §5 and ADR-0005.
- **A general end-user panel builder** — the panel interface is a developer-facing extension point (write a component, register it), not a no-code widget system, by explicit scope decision (`01_SPEC.md` §5).
- **A generalized Capability Registry** — ADR-0008 records this direction but stays `Proposed`; this phase built only the narrower Panel Registry (ADR-0002).
- **The command palette becoming a full command/action surface** — ADR-0007 §6 records this as a future direction; this phase ships only the `/search` results page.
- **"Customize Workbench"/"Manage pinned tools" as command-palette actions** — mentioned in `02_UI.md` §2 but outside this phase's stated FR1/FR12 scope for the nav-rename task that implemented it; deferred as a follow-up, not built.

## Cross-references

- [../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../implementation/Phase-01-Workbench/CURRENT_STATE.md)
- [../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md](../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md)
- [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)
- [BUGS/README.md](BUGS/README.md)
- [QA/README.md](QA/README.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
