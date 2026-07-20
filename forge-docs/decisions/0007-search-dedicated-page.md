# ADR-0007 — Search becomes a dedicated Workbench-reachable page

> **Purpose:** Record adding a dedicated `/search` page, reusing the existing search backend, so "Search" can be a real pinned Workbench tool rather than an alias for the command palette.
> **Scope:** Frontend routing addition only. No backend change.
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted — scope is deliberately limited to a search results page; see §6 for the future direction that was explicitly deferred
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../implementation/Phase-01-Workbench/01_SPEC.md](../implementation/Phase-01-Workbench/01_SPEC.md)
> **Supersedes:** —

---

## 1. Context

`GET /api/search` (`backend/app/services/search/service.py`, `backend/app/api/routes/search.py`) already exists and aggregates matches across secrets, notes, and documents; `frontend/features/search/api.ts` already wraps it for the command palette (⌘K). There is no dedicated `/search` route or page — results only ever appear inside the palette overlay. The project owner's default pinned-tools list names "Search" as a pinnable destination, which requires something routable to pin to.

## 2. Decision

Add a dedicated Search page (route `/search`, query param `?q=`) that reuses the existing `GET /api/search` endpoint and `frontend/features/search/api.ts` — no backend change required. This becomes a legitimate pinnable Workbench tool alongside Secrets, Notes, etc., and the natural destination when a search is broader than the palette's typically-truncated inline results can usefully show.

## 3. Alternatives considered

- Drop "Search" from the default pinned-tools list, since command-palette search already covers the use case — considered, but the project owner's list explicitly included it, and a dedicated results page has independent value (seeing all matches at once) rather than being purely redundant with ⌘K.
- Build a net-new search page backed by a net-new aggregation endpoint — rejected: `global_search()` already aggregates secrets/notes/documents; the actual gap is a missing frontend route, not missing backend capability.

## 4. Consequences

- Makes it easier: "Search" as a pinned tool is real, not aliased; the palette and the dedicated page share one backend contract, keeping "one search" true per [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.7 rather than growing a second implementation.
- Makes it harder / scope note: this is incremental frontend work beyond "Workbench: widgets → panels" alone — one new route, one new page component, reusing existing data. Tracked as a Phase 01 task since it's small and directly required by the approved pinned-tools default, not spun into its own phase.
- Once Vault renames to Secrets (ADR-0006), the search response's `secrets` key/label should be relabeled to match — tracked alongside that rename, not duplicated here.

## 5. Cross-references

- [../implementation/Phase-01-Workbench/01_SPEC.md](../implementation/Phase-01-Workbench/01_SPEC.md)
- [../implementation/Phase-01-Workbench/06_API.md](../implementation/Phase-01-Workbench/06_API.md)
- [0006-vault-renamed-to-secrets.md](0006-vault-renamed-to-secrets.md)
- [0008-capability-registry-direction.md](0008-capability-registry-direction.md)

## 6. Future direction (explicitly deferred, not part of this ADR's scope)

On review, the project owner proposed a much larger long-term destination for Search: not a results page, but Forge's command palette becoming a full VS Code-style command surface (`⌘K` running actions like "Convert PDF," "Open Project Alpha," "Create Workflow" — not just navigating to search results). This is a real direction worth keeping, but it was explicitly **not** approved as Phase 01 scope, for two reasons: (1) it depends on a real command/action registry, which is exactly the generalized system [ADR-0008](0008-capability-registry-direction.md) proposes and defers; and (2) building it now would reopen the "freeze Phase 01" discipline the project owner asked for in the same review.

This ADR's accepted scope remains exactly §2 above: a `/search` results page reusing the existing `GET /api/search` endpoint. The command-palette-as-action-surface idea is recorded here as a pointer, not a commitment — it becomes buildable once [ADR-0008](0008-capability-registry-direction.md) is accepted and a real command registry exists to power it. Do not expand this ADR's scope based on this note without a new decision.
