# ADR-0003 — Single-row persisted layout

> **Purpose:** Record that Workbench's layout (panel visibility/order, pinned tools) persists as one instance-wide row, not per-user or per-device state.
> **Scope:** Persistence model only. Panel contract is ADR-0002 / 12_PANEL_INTERFACE.md.
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
> **Supersedes:** —

---

## 1. Context

Workbench needs to persist which panels are visible, their order, and the pinned-tools list. Forge is single-tenant ([`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.1) — there is exactly one operator — and `AppConfig` (`backend/app/models/app_config.py`) already establishes the pattern of a single-row (`id=1`), instance-wide config table for exactly this kind of setting (theme, master-password hash).

## 2. Decision

Layout is stored as a single-row table (`workbench_layout`, `id=1`) holding JSON-encoded panel and pinned-tool lists, following the same get-or-create pattern `AppConfig` already uses. It is not per-user, per-device, or normalized into child tables with foreign keys.

## 3. Alternatives considered

- Per-browser/per-device layout (e.g. `localStorage` only) — rejected: doesn't survive "same operator, different device on the LAN," a stated user story in `01_SPEC.md` §2, and creates drift between devices.
- Normalized relational tables (`workbench_panel`, `workbench_pinned_tool` with `ORDER BY position`) — rejected for this phase as premature structure for a single-row config blob with at most ~15 total entries. Revisit if panel count or persistence complexity grows materially — tracked as an open TODO in `04_DATABASE.md`.

## 4. Consequences

- Simple migration, simple get/update contract (`03_BACKEND.md` §2, `06_API.md` §1).
- Any future move to per-user layouts requires a real architecture review and its own ADR, per [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.1 — not a casual follow-up.

## 5. Cross-references

- [../implementation/Phase-01-Workbench/04_DATABASE.md](../implementation/Phase-01-Workbench/04_DATABASE.md)
- [../implementation/Phase-01-Workbench/03_BACKEND.md](../implementation/Phase-01-Workbench/03_BACKEND.md)
