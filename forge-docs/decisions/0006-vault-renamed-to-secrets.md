# ADR-0006 — Vault renamed to Secrets, as a compatibility migration

> **Purpose:** Record the rename of the shipped "Vault" feature to "Secrets," and the specific migration shape it must take — a compatibility migration with backward-compatible aliases, not a standalone breaking refactor.
> **Scope:** Naming and migration approach. Does not itself execute the rename in code.
> **Ownership:** Project owner (approved 2026-07-20, refined 2026-07-20)
> **Status:** Accepted
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [ADR-0001](0001-workbench-replaces-dashboard.md)
> **Supersedes:** v0.1.0 of this ADR (standalone-refactor framing, no aliasing)

---

## 1. Context

While defining Workbench's default pinned tools, the project owner specified "Secrets" as a pinned tool. The shipped feature is currently named "Vault" everywhere: `frontend/lib/nav-registry.ts` label and `/vault` route, `frontend/features/vault/`, `backend/app/services/vault/`, `backend/app/models/vault.py`, `backend/app/api/routes/vault.py`, and `ActivityLog.entity_type` values already written to the database. The rename was initially approved as a standalone refactor (v0.1.0 of this ADR). On review, the project owner refined this: the rename should ship as part of Phase 01 as a **compatibility migration**, not a breaking refactor, to avoid stacking migration risk on top of Workbench's own new surface in the same implementation pass.

## 2. Decision

The feature is renamed from "Vault" to "Secrets," executed as a compatibility migration:

- **UI** renames to "Secrets" — sidebar label, page copy, all user-facing text.
- **Routes** rename (`/vault` → `/secrets`); the old `/vault` route redirects to `/secrets` rather than 404ing.
- **Components** rename (`frontend/features/vault/` → `frontend/features/secrets/`).
- **Services** rename (`backend/app/services/vault/` → `backend/app/services/secrets/`).
- **API endpoints** rename (`/api/vault` → `/api/secrets`), with the old path kept as a backward-compatible alias where feasible (proxying to the same handler, not a second implementation).
- **Database artifacts** (table/column names, e.g. `backend/app/models/vault.py`'s `__tablename__`) are renamed **only if it doesn't require a risky data migration**. If a safe in-place rename isn't available (per [`../../docs/Database.md`](../../docs/Database.md) and SQLite's `ALTER TABLE` constraints), the underlying table keeps its current name for now and the rename stays at the application layer (model class name, service module name) — a full physical rename becomes a later, isolated cleanup task, not something Phase 01 risks on.
- **Temporary internal aliases are acceptable** anywhere in the above (e.g. a `services/secrets/` module that thinly wraps or re-exports from what's still physically `services/vault/` internals) until a later cleanup phase removes them. This is a deliberate, temporary exception to [`../07_CODING_STANDARDS.md`](../07_CODING_STANDARDS.md)'s normal no-dead-abstraction expectations, scoped to this migration only.

## 3. Alternatives considered

- Full breaking rename, no aliases, no compatibility period (v0.1.0 of this ADR) — rejected on review: stacks two kinds of risk (Workbench's new surface + a breaking rename of an existing, in-use feature) into one implementation pass, with no fallback if the rename surfaces an issue after the fact.
- Defer the rename entirely to a later, separate phase — rejected: the approved default pinned-tools list already names "Secrets," so some form of the rename is a hard prerequisite for Phase 01's own acceptance criteria (`08_ACCEPTANCE.md` FR13).
- Keep "Vault" as the shipped name, alias "Secrets" only at the UI label level — rejected: still leaves the underlying code permanently out of sync with its own product name, the exact debt this ADR exists to start paying down, just deferred instead of migrated safely.

## 4. Consequences

- Makes it easier: the rename lands within Phase 01's own implementation session without the all-or-nothing risk of a single breaking cutover; a missed reference to the old name degrades to "alias still works," not "broken link."
- Makes it harder / real cost: temporary aliases are debt, explicitly logged as **Known Issues** in [`CURRENT_STATE.md`](../implementation/Phase-01-Workbench/CURRENT_STATE.md) once implementation begins, with an owning future cleanup task — not left to rot silently, per [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.3 (honest gaps over fake completeness).
- If the database table cannot be safely renamed, `backend/app/models/secrets.py`'s `SQLModel` class maps to a table still physically named `vault` (via `__tablename__ = "vault"`) until a later migration — this is intentional, not an oversight, and should be commented in code pointing at this ADR (per [`../07_CODING_STANDARDS.md`](../07_CODING_STANDARDS.md) §5).
- Once the rename lands, the shipped-app docs under `../../docs/` (e.g. `docs/DecisionLog.md`, `docs/Security.md`, `docs/API.md`) should record it there too, including which aliases are temporary — out of scope for this ADR, which only covers the FDK-side decision.

## 5. Cross-references

- [../02_ROADMAP.md](../02_ROADMAP.md)
- [../implementation/Phase-01-Workbench/01_SPEC.md](../implementation/Phase-01-Workbench/01_SPEC.md)
- [../implementation/Phase-01-Workbench/03_BACKEND.md](../implementation/Phase-01-Workbench/03_BACKEND.md)
- [../implementation/Phase-01-Workbench/04_DATABASE.md](../implementation/Phase-01-Workbench/04_DATABASE.md)
- [../implementation/Phase-01-Workbench/06_API.md](../implementation/Phase-01-Workbench/06_API.md)
- [../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md](../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md)
