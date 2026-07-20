# Workbench — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md; the frontend-only panel contract lives in 12_PANEL_INTERFACE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — third full pass (compatibility-migration alias approach), pending confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [03_BACKEND.md](03_BACKEND.md), [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
> **Supersedes:** v0.2.0 of this document (no `/api/vault` compatibility alias)

---

## 1. Endpoints

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| GET | `/api/workbench` | — | `WorkbenchOut` (layout + panel data, see §2) | session required |
| PUT | `/api/workbench/layout` | `WorkbenchLayoutUpdate` | `WorkbenchLayoutOut` | session required |
| POST | `/api/workbench/layout/reset` | — | `WorkbenchLayoutOut` (server default) | session required |

Search is **not** a new backend endpoint — `GET /api/search` (per [ADR-0007](../../decisions/0007-search-dedicated-page.md)) already exists and is reused unchanged by the new `/search` frontend page.

Separately, per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md), the Secrets rename adds one compatibility route: `/api/vault` continues to resolve, proxying to the same handler as `/api/secrets` (not a second implementation), until a later cleanup phase removes it.

> **Note (unchanged from v0.1.0):** `/api/workbench` replaces `GET /api/dashboard` outright, direct cutover, no alias period — this is unrelated to the Secrets alias above, which exists specifically because Vault/Secrets is an established, in-use feature, unlike the brand-new Dashboard→Workbench route.

## 2. Schemas

```python
class WorkbenchPanelState(BaseModel):
    type: str          # opaque panel-type key — NOT a fixed enum, see note below
    visible: bool

class ToolCatalogEntry(BaseModel):
    key: str            # e.g. "ingest", "notes", "secrets", "prompt_studio"
    available: bool      # False for tools belonging to not-yet-built phases

class PinnedTool(BaseModel):
    key: str
    available: bool      # denormalized from ToolCatalogEntry so the Pinned Tools panel
                          # never needs a second request to know a pin is "coming soon"

class WorkbenchLayoutOut(BaseModel):
    panels: list[WorkbenchPanelState]     # full ordered set, whatever was saved — see note below
    pinned_tools: list[PinnedTool]        # ordered, with availability denormalized in
    tool_catalog: list[ToolCatalogEntry]  # every known tool key (available or not) — powers the pin picker

class WorkbenchLayoutUpdate(BaseModel):
    panels: list[WorkbenchPanelState]     # structural validation only, see note below
    pinned_tools: list[str]               # keys only; each must exist in the backend tool catalog (03_BACKEND.md §3)

class WorkbenchData(BaseModel):
    version: str
    storage: StorageStats                 # unchanged shape from the former DashboardData.storage
    recent_activity: list[ActivityEntry]  # unchanged shape
    recent_notes: list[DashboardNote]     # unchanged shape
    # NOTE: no recent_secrets field — removed per 01_SPEC.md §3, requirement 3.

class WorkbenchOut(BaseModel):
    layout: WorkbenchLayoutOut
    data: WorkbenchData
```

**On `WorkbenchPanelState.type` not being an enum:** per [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) and [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md) §7, the backend cannot know which panel types exist in the frontend bundle. `PUT /api/workbench/layout` validates only that every entry has a non-empty `type` string and no duplicates — it does **not** reject an unrecognized `type` (that would reintroduce the coupling ADR-0002 exists to remove). An entry like `{"type": "recent_projects", "visible": false}` is valid and simply renders nothing until Phase 06 registers a matching frontend panel.

`StorageStats` and `ActivityEntry`/`DashboardNote` are carried over unchanged from the former dashboard schemas. No ORM object is ever returned directly, per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §1.1.

## 3. Error handling

| Case | Status | Notes |
|---|---|---|
| No/expired session | 401 | Unchanged from the former dashboard route. |
| `panels` list has a duplicate `type` or an entry missing `type`/`visible` | 422 | Structural validation only — see the note in §2. |
| `pinned_tools` contains a key not in the backend tool catalog (`03_BACKEND.md` §3) | 422 | Unlike `panels.type`, `pinned_tools` keys **are** validated against a known list, since pinning something with no matching catalog entry has no sensible rendering (not even a "coming soon" state, which requires the key to be *known but unavailable*). |
| Layout row somehow missing on `GET` | — | Not an error case — `get_layout()`'s get-or-create behavior prevents this from surfacing. |

## 4. Rate limiting / abuse considerations

None beyond the existing deployment-level posture in [`../../../docs/Security.md`](../../../docs/Security.md) — no outbound network calls, no new attack surface beyond validated instance-config writes.

## 5. TODO

- [ ] TODO: Confirm the direct-cutover assumption in §1's note before implementation removes `/api/dashboard`.
- [ ] TODO: Finalize the backend tool catalog (§2 `tool_catalog`) contents once [`03_BACKEND.md`](03_BACKEND.md) §3's `WORKBENCH_TOOL_KEYS` constant is confirmed — key naming is resolved (`"secrets"`, not `"vault"`, per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)); remaining work is just confirming the constant's exact contents.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
