# ADR-0001 — Workbench replaces Dashboard

> **Purpose:** Record that Dashboard is retired as a concept, not just relabeled, and Workbench is its sole successor.
> **Scope:** Naming and identity of the app's home surface only. Panel mechanics are ADR-0002.
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../implementation/Phase-01-Workbench/01_SPEC.md](../implementation/Phase-01-Workbench/01_SPEC.md)
> **Supersedes:** —

---

## 1. Context

The initial Phase 01 draft framed the new home experience as "Dashboard with widgets" — an evolution of the existing Dashboard feature, keeping the Dashboard name. `01_SPEC.md` §6 flagged this as an open question: keep "Dashboard" as the user-facing label while "Workbench" stays an internal/phase name, or rename outright. The project owner determined this framing undersells the ambition — Workbench is meant to be the user's primary workspace, not a read-only status page with a new name attached.

## 2. Decision

Dashboard is retired as a concept entirely. Workbench is the only home-experience concept, at the same route (`/`), sidebar position, and shortcut (`D`) Dashboard held. There is no dual "Dashboard vs. Workbench" naming split anywhere in the app or its docs going forward.

## 3. Alternatives considered

- Keep "Dashboard" as the user-facing label, "Workbench" as an internal/phase name only — rejected: creates a permanent split between what users see and what the codebase and docs call it, the exact problem being avoided.
- Ship Workbench as a new, separate route alongside the existing Dashboard — rejected: fragments the home experience into two entry points, against the "one canonical surface per concern" spirit of [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.7.

## 4. Consequences

- Every forward-looking reference to "Dashboard" (sidebar label, command-palette entry, docs) becomes "Workbench." Historical references describing the pre-Phase-01 code (`dashboard.py`, `frontend/features/dashboard/`) remain accurate as a description of prior state, not a live name.
- Resolves the open question in `01_SPEC.md` §6.
- The `backend/app/services/dashboard.py` → `workbench.py` rename in `03_BACKEND.md` §1 is now a ratified decision, not a proposal.

## 5. Cross-references

- [../implementation/Phase-01-Workbench/01_SPEC.md](../implementation/Phase-01-Workbench/01_SPEC.md)
- [../implementation/Phase-01-Workbench/02_UI.md](../implementation/Phase-01-Workbench/02_UI.md)
- [../implementation/Phase-01-Workbench/03_BACKEND.md](../implementation/Phase-01-Workbench/03_BACKEND.md)
