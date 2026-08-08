# Frontend Reimagine — Verification Contract

> **Purpose:** The machine-verifiable contract the Verification Orchestrator operates against for this phase — see [`../../15_VERIFICATION_FRAMEWORK.md`](../../15_VERIFICATION_FRAMEWORK.md) §5.
> **Scope:** This phase only.
> **Status:** **Satisfied — RC verified 2026-08-07.** Scope resolved by **OQ4** ([`01_SPEC.md`](01_SPEC.md) §7) at the 2026-08-06 authorization review; every item below re-checked live at Release Candidate verification, not carried forward from milestone-time citations.
> **Version:** 0.2.0
> **Last Updated:** 2026-08-07
> **Depends On:** [01_SPEC.md](01_SPEC.md), [07_TESTING.md](07_TESTING.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md), [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md), [11_SCREEN_GRAPH.md](11_SCREEN_GRAPH.md), [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)

---

## 0. What this contract deliberately does not verify — OQ4's resolution

Phase 09 is a **presentation-layer phase in a codebase with no frontend test framework**. That combination makes a naive verification contract actively misleading: an Orchestrator that reports PASS on a phase whose central claims are visual would be asserting something it cannot see.

The resolution, approved 2026-08-06, is to scope this contract to the **objectively checkable subset** and route everything else to human or tooling gates that can actually judge it.

| Claim | Verified by |
|---|---|
| Types, lint, build, backend suite | **This contract** (§5) |
| Route resolution, redirects, deep links, all 48 navigation edges | **This contract** (§5.1) |
| Computed font-family and `--font-sans`/`--font-mono` resolution | **This contract** (§5.2) — the 🔴 defect, asserted mechanically |
| Zero backend diff, no new dependency, no parallel architecture | **This contract** (§4, §6) |
| Visual hierarchy, spacing rhythm, aesthetic fidelity, "AI-slop" absence | `/design-review` at T30 — **not this contract** |
| Contrast ratios, focus order, screen-reader behavior | T27 accessibility pass + a QA ticket — **not this contract** |
| "The interface feels coherent" | Project-owner sign-off — **not this contract** |

A PASS from this contract means *nothing regressed and the mechanical claims hold*. It does **not** mean the redesign is good. Those are different questions and this phase keeps them separate on purpose.

## 1. Phase Metadata

- **Phase name:** Frontend Reimagine (Phase 09)
- **Phase objective:** Reimagine the presentation layer of the Forge frontend in place — one coherent visual language, one coherent information architecture, one deliberate application shell — while preserving every existing route, API contract, user flow, and product capability exactly.
- **Dependencies:** Phases 01–08, all Released or Frozen. No blocking dependency.
- **Completion definition:** [`README.md`](README.md) → Definition of Complete.

## 2. Required Tasks

Referenced by ID, not restated, so this contract cannot drift from the task list.

- [x] T0, T0.5, T0.6 — Milestone 0 (baseline, foundation defects, corrected baseline)
- [x] T1–T8 — Milestone 1 (foundation)
- [x] T9–T13 — Milestone 2 (primary surfaces)
- [x] T14–T22 — Milestone 3 (secondary surfaces)
- [x] T23–T25 — Milestone 4 (consolidation)
- [x] T26–T30 — Milestone 5 (validation)

Source of truth: [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## 3. Acceptance Criteria

All of [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) AC1–AC56, referenced by ID. Each is independently validated; none is inferred from another passing.

**Machine-verifiable by the Orchestrator:** AC1, AC3, AC5, AC7–AC13, AC15, AC17, AC19, AC22, AC24, AC25, AC26, AC47, AC48, AC50, AC51, AC54, AC55, and the mechanically-measurable subset of AC56 (rail widths, topbar height, row heights, dialog tiers, control heights — all readable as computed values).
**Verified by AC2's runtime measurement:** AC2, AC43 (computed style / emulated media query).
**Routed to `/design-review`, the a11y pass, or owner sign-off:** AC4, AC6, AC14, AC16, AC18, AC20, AC21, AC23, AC27–AC42, AC44–AC46, AC49, AC52, AC53.

## 4. Expected File Scope

**Expected new/modified:**
- `frontend/app/**` — `globals.css`, `layout.tsx`, all 17 route files
- `frontend/components/**` — primitives, shared components, app-shell, command-palette
- `frontend/features/**` — presentation only
- `frontend/lib/nav-registry.ts` — **additive only**
- `frontend/next.config.ts` — one rewrite added (T0.5b)
- `frontend/package.json` — removals only (`framer-motion`, per OQ3)
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/**`, `forge-docs/04_UI_GUIDELINES.md`, `forge-docs/05_DESIGN_SYSTEM.md`, `forge-docs/history/**`

**Explicitly out of scope — the Architecture Verifier reports any change here as unexpected:**
- `backend/**` — **zero diff required.** See [`03_BACKEND.md`](03_BACKEND.md).
- `docker/**` — read-only inspection at T0.5b; a needed change is a finding, not an edit.
- `frontend/lib/api-client.ts` — the fetch boundary is unchanged.
- `frontend/features/*/api.ts` — no endpoint, shape, or query-key change.
- Any frozen phase's `forge-docs/implementation/Phase-0[1-8]-*/` specification.

## 5. Required Validation Commands

- [x] `cd frontend && npx tsc --noEmit` — zero errors, re-run at RC 2026-08-07
- [x] `cd frontend && npm run lint` — zero errors, re-run at RC 2026-08-07
- [x] `cd frontend && npm run build` — succeeds, all 17 static routes + `/projects/[id]` dynamic route compile, re-run at RC 2026-08-07
- [x] `cd backend && pytest` — green **and unchanged** — full suite run at RC (not just diffed): 100% pass, zero failures, only pre-existing deprecation warnings
- [x] `git diff --stat backend/` — **empty**, re-confirmed at RC 2026-08-07 (checked `docker/` alongside it, also empty)
- [x] `docker compose build` — **succeeds**, run at RC 2026-08-07: both `forge-frontend` and `forge-backend` images built clean (this had not been run earlier in the phase; `docker/**` being inspect-only governs *editing* docker files, not verifying the existing compose config still builds)

### 5.1 Navigation-edge assertions

Not routes — **edges**, exercised from their real source screens, per [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) §7. All 48, compared against the T0 baseline:

- [x] 17 routes resolve 200, no console error — re-confirmed at RC via curl sweep, 2026-08-07
- [x] 5 compatibility redirects land on their correct targets — re-confirmed at RC, all 307 to correct destinations
- [x] 3 auth transitions + 2 lock paths — topbar Lock verified live (T28); palette Lock verified by code equivalence (identical `authApi.lock()` + redirect call, session unlock is intentionally unavailable to automated verification per `07_TESTING.md` §2.2)
- [x] 12 palette nav targets + 4 palette result deep links — all 8 advertised shortcuts verified at T4/T28 (including the K-collision fix); live search results and their deep-links (secrets/notes/documents) verified at T28
- [x] 3 Workbench quick actions + 7 pinned-tool targets + 2 panel deep links — pinned-tool catalog re-verified at T28 via the Pin Picker (all 7 resolve); quick actions and panel deep-links carried unchanged from pre-phase (presentation-only migration, no logic touched)
- [x] 4 project-detail scoped links + 1 project → model-playground link — the 3 `?project_id=` "View all" links + `/projects` breadcrumb verified live at T28; the "project → model-playground link" is an inline Run panel on the project detail page, not a separate navigation edge — confirmed present and functional
- [x] 2 Knowledge result targets (including the AC54 `?open=` fix) — verified live at T28 (documents and notes result links)
- [x] 3 Search result targets — verified live at T28 (`/search?q=AWS` → secret result link)
- [x] 9 deep-link parameter contracts per [`06_API.md`](06_API.md) §3.1 — all verified per `08_ACCEPTANCE.md` AC9

### 5.2 Runtime style assertions

- [x] Computed `font-family` on `<html>` and `<body>` resolves to Geist, both themes — re-measured at RC 2026-08-07
- [x] `--font-sans` and `--font-mono` both non-empty — re-measured at RC, both resolve to the full Geist/Geist Mono font stacks
- [x] `fetch('/system/status')` returns 200 with `application/json` *(pre-phase: 404, `text/html`)* — re-confirmed 200 at RC
- [x] Under emulated `prefers-reduced-motion: reduce`, transition durations collapse — live-verified at RC: with the preference active, a sidebar link's computed `transitionDuration` measured `1e-05s` and `--duration-normal` measured `0s`. (This assertion was incorrectly marked unverified in the T29 documentation pass — corrected here.)

## 6. Architecture Constraints

From [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2 and [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md):

- [x] **Zero backend diff.** No service, router, schema, model, or migration touched — re-confirmed empty at RC.
- [x] **`lib/api-client.ts` remains the only JSON fetch boundary.** Re-grepped at RC: exactly 2 raw `fetch(` calls in `frontend/features/**/*.ts`, both the documented binary-download exceptions (`documents/api.ts` export, `project-init/api.ts` download) — zero raw JSON-GET fetches.
- [x] **No cross-feature import count increase** (AC55). Re-counted at RC by grepping every `from "@/features/` import: exactly 10 distinct file→feature edges, matching the frozen baseline exactly.
- [x] **No parallel architecture** — confirmed via T25's sweep and RC's directory review; no second shell, router, API client, or page directory.
- [x] **No primitive API change** — every `components/ui/*` export name and prop signature preserved (T5 retuned styling only; T25 removed 3 zero-consumer primitives).
- [x] **`NAV_ITEMS` additive only** — `group` field added at T3; no `href`/`title`/`icon`/`shortcut`/`description` value changed.
- [x] **No new runtime dependency.** One (`framer-motion`) net-removed at T25; re-confirmed zero import sites at RC.
- [x] ADR constraints: [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md) (no search scope change, no route removed — confirmed, `/search` still covers secrets+notes+documents), [ADR-0017](../../decisions/0017-layered-design-token-architecture.md) (every shadcn token name preserved), [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) (panel registry contract intact — pinned-tool catalog re-verified at T28).

## 7. Documentation Requirements

All unconditional, per the template's no-conditionals rule:

- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) — reflects reality, no stale "In Progress" beyond the owner-sign-off gate itself
- [x] [`10_RELEASE_NOTES.md`](10_RELEASE_NOTES.md) — finalized at T29, corrected at RC (reduced-motion claim restored, two new partial-coverage limitations added)
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) — every criterion checked with cited evidence; re-verified live at RC rather than trusting T29's citations, which surfaced and corrected one documentation error (AC43) and two new honest partial-coverage findings (AC41, AC45)
- [x] [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — every task (T0–T30) checked with as-built notes
- [x] [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) — §3's minimum-viewport TODO, §4's contrast-standard and audit TODOs, and §6's motion-policy TODO all resolved into fact
- [x] [`../../05_DESIGN_SYSTEM.md`](../../05_DESIGN_SYSTEM.md) — typography, spacing/breakpoints, primitive-inventory, and motion TODOs resolved into fact (full color-palette table remains a standing, non-blocking TODO)
- [x] [`../../history/`](../../history/) — checkpoint entries exist for the discovery and authorization milestones; per-milestone entries for Milestones 1–5 live as session notes in `CURRENT_STATE.md` rather than separate `history/` files (consistent with how this phase has recorded milestone narrative throughout — not a gap introduced at RC)

## 8. Cross-references

- [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md) · [../VERIFICATION_CONTRACT_TEMPLATE.md](../VERIFICATION_CONTRACT_TEMPLATE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [07_TESTING.md](07_TESTING.md) · [11_SCREEN_GRAPH.md](11_SCREEN_GRAPH.md) · [IMPLEMENT.md](IMPLEMENT.md)
