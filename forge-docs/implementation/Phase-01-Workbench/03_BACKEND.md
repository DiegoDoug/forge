# Workbench — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md; the frontend panel contract lives in 12_PANEL_INTERFACE.md (the backend has no equivalent concept — see §1 note).
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — third full pass (compatibility-migration alias approach), pending confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_SPEC.md](01_SPEC.md), [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md), [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md), [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
> **Supersedes:** v0.2.0 of this document (Secrets rename treated as a flat rename with no aliasing)

---

## 1. Service boundary

Rename and extend the existing service, in place: `backend/app/services/dashboard.py` → `backend/app/services/workbench.py`, and `backend/app/api/routes/dashboard.py` → `backend/app/api/routes/workbench.py` (per [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md)). This stays a single module, not a new `services/workbench/` subpackage.

**Important architectural note:** the *panel* concept ([`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md)) is a frontend-only construct — which panels exist is determined by what's compiled into the frontend bundle and registered, which the backend cannot see or enumerate. The backend's job is narrower than "know about panels": it persists an opaque, structurally-validated list of `{type, visible}` entries and otherwise stays agnostic to what any `type` string means. This is a deliberate consequence of [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) — see §2 below.

Two companion pieces of backend-adjacent work are prerequisites for this phase's default pinned-tools set to be real, per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md) and [ADR-0007](../../decisions/0007-search-dedicated-page.md):

- **Vault → Secrets rename, as a compatibility migration** (per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)): `backend/app/models/vault.py` → `secrets.py`, `backend/app/services/vault/` → `secrets/`, `backend/app/api/routes/vault.py` → `secrets.py`, with `/api/vault` kept as a route alias proxying to the same handler as `/api/secrets` (not a duplicate implementation) rather than removed. The underlying database table is renamed only if that's a safe, non-risky migration; if not, the `Secrets` `SQLModel` class keeps `__tablename__ = "vault"` for now, commented with a pointer to ADR-0006, until a later cleanup phase can do a full physical rename. Tracked as a prerequisite task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — it's a migration of existing, already-specified functionality, not new backend design.
- **Search page:** no backend change — `GET /api/search` (`backend/app/services/search/service.py`) already exists and is reused as-is.

## 2. Business logic

- `get_workbench(session)` — returns the same aggregate data `get_dashboard()` returns today (storage, recent activity, recent notes, version — **recent secrets is dropped entirely**, not just made optional), **plus** the current layout (panel visibility/order, pinned tools). One response backs the whole page load (see [`06_API.md`](06_API.md) §1).
- `get_layout(session)` — fetches the single `WorkbenchLayout` row (id=1), creating it with default values on first access if it doesn't exist yet — mirrors the `get_config()` get-or-create pattern already used by `backend/app/services/settings/service.py` for `AppConfig`.
- `update_layout(session, panels, pinned_tools)` — replaces the layout in one call (whole-object update). Validates, per [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §7:
  - Every `panels` entry has a non-empty string `type` and boolean `visible`, with no duplicate `type` values. **The backend does not check `type` against a fixed catalog** — panel existence is a frontend-registry fact it has no visibility into (see §1 note).
  - Every pinned-tool identifier is present in a backend-side tool catalog — see §3 below for its shape, which now must include forward-looking, not-yet-implemented tools.
- `reset_layout(session)` — overwrites the row with the server-owned `DEFAULT_LAYOUT` constant: panels `["pinned_tools", "recent_activity", "quick_actions", "system_status", "recent_notes"]` (all visible, in that order — `recent_projects` is deliberately absent from the default panel list per [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md), since nothing renders it yet), and pinned tools `["ingest", "notes", "prompt_studio", "universal_converter", "secrets", "search"]`.

## 3. Integration with existing services

- Reuses `app.services.notes.service` for the Recent Notes panel's data, exactly as `get_dashboard()` does today. **No longer calls `vault.service.list_secrets`** — Recent Secrets is removed (see §2).
- Reads `ActivityLog` directly via the same query `get_dashboard()` already runs.
- **New: a backend-side tool catalog** — `WORKBENCH_TOOL_KEYS`, a dict (not a flat set, since forward-looking entries need a status flag), e.g.:

  ```python
  WORKBENCH_TOOL_KEYS = {
      "secrets": {"available": True},              # per ADR-0006 — the rename lands as the first
                                                     # implementation task, so this constant is
                                                     # authored with "secrets" from the start, not "vault"
      "notes": {"available": True},
      "documents": {"available": True},
      "generators": {"available": True},
      "crypto": {"available": True},
      "converters": {"available": True},
      "utilities": {"available": True},
      "ingest": {"available": True},
      "search": {"available": True},              # new, per ADR-0007
      "prompt_studio": {"available": False},       # Phase 03, not yet built
      "universal_converter": {"available": False}, # Phase 04, not yet built
  }
  ```

  This resolves [`01_SPEC.md`](01_SPEC.md) §6's now-closed "disabled pin representation" question: the backend allowlist itself carries the `available` flag, which `WorkbenchLayoutOut` echoes per pinned tool (see [`06_API.md`](06_API.md) §2) so the frontend never needs its own separate forward-looking catalog. If the compatibility alias (`/api/vault`) is still live when this constant is written, it does not get its own `"vault"` catalog entry — a pinned tool always refers to the current name; the alias only keeps the *route* working for anything still linking to the old path.
- This constant is kept in `backend/app/services/workbench.py`, manually synced with `frontend/lib/nav-registry.ts` — the same known, tracked gap called out in v0.1.0 of this document; unchanged by the panel-architecture rewrite.

## 4. Architectural compliance

- [x] Routers stay thin — `routes/workbench.py` only wires request/response schemas to `services/workbench.py` calls.
- [x] No cross-feature imports beyond existing aggregator precedent (`dashboard.py` already read from Notes/Vault/Activity; this phase narrows that to Notes/Activity).
- [x] No new external dependency.
- [ ] TODO: confirm the rename (`dashboard.py` → `workbench.py`, `/api/dashboard` → `/api/workbench`) — same direct-cutover assumption as v0.1.0, unchanged by this revision.

## 5. TODO

- [ ] TODO: Confirm the tool-catalog `available` flag design in §3 is the right mechanism before implementation — alternative considered: a fully separate "roadmap tools" list the frontend hardcodes, rejected here as a second source of truth duplicating what the backend already needs to validate against.
- [ ] TODO: Sequence the Vault → Secrets rename (§1) as the first task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md), ahead of anything that references the `secrets` tool key.
- [ ] TODO: Confirm the pinned-tool allowlist duplication with `nav-registry.ts` (§3, last paragraph) is an acceptable known gap for this phase.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
- [../../decisions/0007-search-dedicated-page.md](../../decisions/0007-search-dedicated-page.md)
