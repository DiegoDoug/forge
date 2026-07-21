# Workbench — README

> **Purpose:** Entry point for the Workbench phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Implementation Complete — Pending: QA ([`QA/`](QA/README.md)), Owner Sign-off ([`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §8), Merge
> **Version:** 0.5.0
> **Last Updated:** 2026-07-21
> **Depends On:** [01_SPEC.md](01_SPEC.md), [../../decisions/README.md](../../decisions/README.md), [../../decisions/0009-phase-specification-freeze.md](../../decisions/0009-phase-specification-freeze.md)
> **Supersedes:** v0.3.0 of this document (awaiting authorization; no Definition of Success; single flat milestone list instead of the 4-milestone checkpoint plan)

---

## Objective

Give Forge a configurable home workspace — the **Workbench** — that surfaces pinned tools, recent activity across every feature, and quick actions, fully replacing the former Dashboard concept (not just evolving it — see [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md)). Workbench is a panel *runtime*: it renders any component implementing the `WorkbenchPanel` interface ([`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md)), so future phases add their own presence without touching Workbench's own code ([ADR-0002](../../decisions/0002-workbench-panel-architecture.md)).

## Scope

**In scope:**
- The Workbench panel runtime and its five active panels (Pinned Tools, Recent Activity, Quick Actions, Storage & System, Recent Notes).
- The `WorkbenchPanel` interface and panel registry.
- Customization: show/hide, reorder, pin/unpin tools, reset to default — all persisted server-side.
- The Vault → Secrets **compatibility migration** ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md) — renamed UI/routes/components/services/API with backward-compatible aliases, not a breaking cutover) and the new dedicated `/search` page ([ADR-0007](../../decisions/0007-search-dedicated-page.md)), as prerequisites the approved default pinned-tools list depends on.

**Out of scope:**
- Implementing Prompt Studio, Universal Converter, Model Playground, Knowledge Hub, or Projects themselves — see [`01_SPEC.md`](01_SPEC.md) §5.
- A `RecentProjectsPanel` implementation — the panel `type` is defined (per [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md)) but stays unregistered/inactive until Phase 06.
- Per-user/per-device layouts (single-tenant, [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.1).
- A general end-user panel builder — the panel interface is a developer-facing extension point, not a no-code widget builder.
- **Workflows, in any form** — Phase 01 delivers Workbench, its panels, the layout system, and the Panel Registry, and nothing else, by explicit project-owner decision.
- **A generalized Capability Registry** — [ADR-0008](../../decisions/0008-capability-registry-direction.md) is `Proposed`, not `Accepted`; Phase 01 builds the narrower Panel Registry ([ADR-0002](../../decisions/0002-workbench-panel-architecture.md)) only.
- **A Projects interface** (`ProjectProvider`/`ProjectContext`/Global-vs-Project Mode) — [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) keeps this in Phase 06.
- **The command palette becoming a full command/action surface** — [ADR-0007](../../decisions/0007-search-dedicated-page.md) §6 records this direction; Phase 01 ships the `/search` results page only.

## Relationship to the shipped application

Fully replaces the former **Dashboard** feature (`frontend/features/dashboard/`, `backend/app/services/dashboard.py`) — this is a ratified decision ([ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md)), not a proposal awaiting confirmation.

- Related frontend: `frontend/features/dashboard/` (removed), `frontend/features/workbench/` (new), `frontend/features/vault/` → `frontend/features/secrets/` (renamed, per ADR-0006), `frontend/features/search/` (existing, reused by the new `/search` page).
- Related backend: `backend/app/services/dashboard.py` → `workbench.py`, `backend/app/models/vault.py` → renamed per ADR-0006.

## Deliverables

- [x] The Workbench runtime (`WorkbenchGrid`, `WorkbenchPanelCard`, panel registry) per [`05_COMPONENTS.md`](05_COMPONENTS.md) and [`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md). (T9)
- [x] Five active panels, each registered through the panel registry, per [`05_COMPONENTS.md`](05_COMPONENTS.md) §1.2. (T11)
- [x] `workbench_layout` table + Alembic migration, per [`04_DATABASE.md`](04_DATABASE.md). (T3)
- [x] `GET/PUT/POST /api/workbench*` endpoints, per [`06_API.md`](06_API.md). (T7)
- [x] The Vault → Secrets rename, per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md). (T1)
- [x] The new `/search` page, per [ADR-0007](../../decisions/0007-search-dedicated-page.md). (T2)
- [x] Removal of `frontend/features/dashboard/` and the old `/api/dashboard` route. (T14)

## Dependencies

None on other new phases — this remains the entry-point phase. It does carry two internal prerequisite tasks (the Secrets rename and the Search page) that must land before or alongside the panel/layout work, per [`01_SPEC.md`](01_SPEC.md) §6.

## Milestones

Four milestones, matching [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)'s task grouping exactly — see [`IMPLEMENT.md`](IMPLEMENT.md) "Milestone Plan" for the authoritative version:

- [x] Milestone 1 — **Foundation** (T1–T4): Secrets compatibility migration, `/search` page, `workbench_layout` migration, the panel contract itself.
- [x] Milestone 2 — **Backend** (T5–T8): layout persistence service, workbench data aggregation, API routes, backend tests.
- [x] Milestone 3 — **Frontend** (T9–T12): the Workbench runtime shell, pin picker, all five active panels, drag/keyboard reorder and panel states.
- [x] Milestone 4 — **Integration** (T13–T16): nav rename, old Dashboard removal, manual verification, accessibility scan.

> Each milestone completion is a checkpoint trigger, in addition to the standard 10–12 task / ~70% context triggers — see [`IMPLEMENT.md`](IMPLEMENT.md) "Milestone Plan" and [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- **Technical:** the panel-type-not-enum-validated design ([ADR-0002](../../decisions/0002-workbench-panel-architecture.md)) trades backend safety for extensibility — a typo'd panel `type` in a future phase silently renders nothing rather than erroring loudly; mitigated by the regression test in [`07_TESTING.md`](07_TESTING.md) §1, not eliminated.
- **Product/UX:** "coming soon" pinned tiles (Prompt Studio, Universal Converter) risk feeling like unfinished work if not visually clear — see [`02_UI.md`](02_UI.md) §3.4.
- **Existing features touched:** the Vault → Secrets rename is a real rename of shipped, in-use functionality — see the regression risk noted in [`07_TESTING.md`](07_TESTING.md) §4.

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [ ] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off. — Two criteria are deliberately not: QA-0001/QA-0002 (drag FPS/Profiler, live screen-reader pass), ruled non-blocking for sign-off by the project owner and tracked in [`QA/`](QA/README.md) rather than checked off without evidence.
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items. — Status is explicitly "Implementation Complete — Pending: QA, Owner Sign-off, Merge," not "Done."
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).
- [ ] **Not yet done, and not part of the original Definition of Complete, but required before merge per the project owner:** owner sign-off (`08_ACCEPTANCE.md` §8) and disposition of the 5 findings from the post-implementation audit (see [`POST_IMPLEMENTATION_REVIEW.md`](POST_IMPLEMENTATION_REVIEW.md) and `CURRENT_STATE.md`'s "Known Issues").

## Definition of Success

The full, checklist-format pass/fail criteria live in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md); this is the plain-language version the project owner set as the bar:

- The application still builds cleanly.
- Docker starts without manual intervention.
- Every existing feature continues to function.
- The Dashboard has become the Workbench.
- Panel registration works.
- Layout persistence works.
- The Search page exists.
- The Secrets migration is complete, with compatibility aliases in place.
- No scope violations were introduced (per [ADR-0009](../../decisions/0009-phase-specification-freeze.md) — no capability registry, no `ProjectProvider`, no workflow code, no extra panels).
- The implementation passes all documented acceptance tests.

**If one optional enhancement is left out but the system is stable, that is preferable to introducing unstable or speculative architecture.** When in doubt during implementation, resolve toward this list and the Priority Order in [`IMPLEMENT.md`](IMPLEMENT.md), not toward doing more.

## Exit Criteria (before `IMPLEMENT.md` is authorized)

Per the project owner's direction, `IMPLEMENT.md` is **not** authorized for this phase until every item below is true:

- [x] `01_SPEC.md` — specification complete.
- [x] `02_UI.md` — UI contract complete.
- [x] `03_BACKEND.md` — backend contract complete.
- [x] `04_DATABASE.md` — database contract complete.
- [x] `12_PANEL_INTERFACE.md` — panel interface contract created.
- [x] `06_API.md` — API contract finalized.
- [x] `07_TESTING.md` — testing strategy approved.
- [x] `08_ACCEPTANCE.md` — acceptance criteria finalized (including performance, accessibility, and extensibility criteria).
- [x] [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md) through [ADR-0007](../../decisions/0007-search-dedicated-page.md) — all `Status: Accepted`.

All nine are content-complete as of 2026-07-20, across three review passes with the project owner (initial spec → panel-architecture rewrite → scope-freeze and compatibility-migration refinements). Deliberately **not** required, and correctly absent from this list: [ADR-0008](../../decisions/0008-capability-registry-direction.md) (Capability Registry), which stays `Proposed` by design — see `01_SPEC.md` §5 and §6.

## Authorization

**Phase 01 — Workbench**

- **Status:** ✅ Authorized
- **Specification:** 🔒 Locked (per [ADR-0009](../../decisions/0009-phase-specification-freeze.md) — bug fixes, clarifications, and typos allowed; new features, architectural changes, and scope expansion deferred to the backlog until this phase reaches Definition of Done)
- **Implementation:** ✅ Approved to begin

Authorized by the project owner on 2026-07-20, after three specification review passes and nine accepted (plus one deliberately deferred) ADRs. From this point forward, the specification is the contract: `IMPLEMENT.md` governs execution, [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) governs the work breakdown, and [ADR-0009](../../decisions/0009-phase-specification-freeze.md) governs what may change along the way. New ideas surfaced during implementation are captured as roadmap items or future ADRs, not folded into this phase.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [QA/README.md](QA/README.md)
- [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../decisions/README.md](../../decisions/README.md)
- [../../decisions/0009-phase-specification-freeze.md](../../decisions/0009-phase-specification-freeze.md)
