# Frontend Reimagine — README

> **Purpose:** Entry point for the Frontend Reimagine phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **Release Candidate verified, 2026-08-07. Ready for owner sign-off.** All six milestones (T0–T30) complete — see [`IMPLEMENT.md`](IMPLEMENT.md) and [`CURRENT_STATE.md`](CURRENT_STATE.md). The 🔴 typography BLOCKER is fixed and live-verified. Two non-blocking Should Fix items and two partial-coverage accessibility findings are recorded in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §12 for the owner's sign-off decision; none are Phase 09 regressions.
> **Last Updated:** 2026-08-07

---

## Objective

Reimagine the presentation layer of the Forge frontend in place — one coherent visual language, one coherent information architecture, one deliberate application shell — while preserving every existing route, API contract, user flow, and product capability exactly.

The guiding constraint, stated as a test: *a user familiar with Forge today must recognize the same product and find every capability where they expect it, while experiencing a substantially more coherent and professional interface.*

## Scope

**In scope — all delivered, T0–T30:**
- [x] A three-layer design-token system merged into `frontend/app/globals.css`, preserving every existing shadcn token name ([ADR-0017](../../decisions/0017-layered-design-token-architecture.md)).
- [x] Fixing the 🔴 typography defect that renders the entire application in Times New Roman ([`00_AUDIT.md`](00_AUDIT.md) §3.1). Live-verified at RC: `--font-sans`/`--font-mono` resolve to Geist/Geist Mono everywhere.
- [x] A real application shell owning layout, shell-height, and scroll containment.
- [x] Grouped navigation (Workspace / Library / Build / Tools + Settings as utility) rendered from one source for both rail and drawer ([ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md)).
- [x] A resolved search model: ⌘K palette as the universal entry point, `/search` as its full-results view, Knowledge Hub as a domain browser — **all three keeping their current scope**.
- [x] Implementation of the eight `NAV_ITEMS[].shortcut` accelerators the palette already displays but does not bind. (One self-collision — Knowledge's "K" vs. the palette's own toggle key — found and fixed at T28.)
- [x] Retune of all 40 `components/ui/*` primitives onto the token system, with **every export name and prop signature preserved**.
- [x] New shared components replacing patterns duplicated 4–7 times: `DataList`, `FilterRail`, `SearchField`, `ErrorState`, `ConfirmDialog`, `Toolbar`, `StatusBadge`, and others ([`05_COMPONENTS.md`](05_COMPONENTS.md)).
- [x] Redesign of all 17 routes, each covering loading / empty / filtered-empty / populated / error / destructive states.
- [x] Genuine responsive behavior at 375 / 768 / 1024 / 1440 — behavior changes, not size changes. (One systemic layout bug on Secrets/Documents found and fixed at T30 — see `CURRENT_STATE.md` Known Issue #22.)
- [x] A WCAG 2.1 AA baseline in both themes, including accessible names on all 38 icon-only buttons and a `prefers-reduced-motion` block. Both delivered; the reduced-motion block is live-verified working. Two related items (dialog focus-restore, uniform form-error wiring) are partial — see `08_ACCEPTANCE.md` AC41/AC45.
- [x] Uniform destructive-action confirmation across every delete in the app.
- [x] One `next.config.ts` rewrite so the existing `/system/status` endpoint stops 404-ing in development ([`00_AUDIT.md`](00_AUDIT.md) §3.2). The equivalent production gap (`docker/nginx.conf`) was found, raised, and tracked in `docs/Roadmap.md` rather than patched — `docker/**` was inspect-only under this phase's contract.
- [x] Removal of dead code: unused primitives, duplicated inline patterns, and the `framer-motion` dependency (removed).

**Out of scope — held throughout, verified at RC:**
- [x] **Any backend change** — confirmed: `git diff --stat backend/ docker/` empty at every milestone boundary and again at final RC verification.
- [x] **Any new product capability** — none added.
- [x] **Route removal.** No route was deleted. `/search` kept its URL *and* its full secrets+notes+documents scope.
- [x] Changes to the auth/session model, the TanStack Query data layer, `lib/api-client.ts`, or per-feature `api.ts` ownership — none made.
- [x] List-endpoint pagination — remains a tracked backend gap in [`../../../docs/Roadmap.md`](../../../docs/Roadmap.md), not solved here, as planned.
- [x] Introducing a frontend test framework — not introduced; regression safety rested on the T0 baseline, typecheck/lint/build, and disciplined manual + live verification throughout, as planned.
- [x] Any new runtime dependency — none added; one (`framer-motion`) net-removed.
- [x] Reopening the specification of any frozen phase (01–08) — none reopened; all touches were presentation-only.

## Relationship to the shipped application

This phase touches **every** frontend surface, which makes it unlike any prior phase. It touches **no** backend surface, which makes it smaller than most.

- Related frontend: all of `frontend/app/`, `frontend/components/`, `frontend/features/`, `frontend/lib/`.
- Related backend: **none modified.** `next.config.ts` gains one rewrite so an already-shipped endpoint becomes reachable.

## Deliverables

- [x] Token system in `globals.css`, with the typography defect fixed — verified by computed style at RC, not by eye.
- [x] `AppShell` + grouped `Sidebar`/`MobileNav` + reworked `Topbar` + reworked `CommandPalette`.
- [x] Retuned primitive layer and the new shared component set.
- [x] 17 redesigned routes with full state coverage.
- [x] Zero *regressions* against every criterion in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) — every AC evidenced; a small number are partial-coverage findings rather than regressions (see AC41/AC45), none blocking.
- [x] `04_UI_GUIDELINES.md` and `05_DESIGN_SYSTEM.md` updated — this phase converted several of their standing TODOs (contrast standard, typography/spacing/breakpoints, primitive inventory, motion) into fact.

## Dependencies

None blocking. Every phase this depends on (01–08) is Released or Frozen.

- [x] **Owner ratification granted 2026-08-06.** Phase 09 did not exist in [`../../02_ROADMAP.md`](../../02_ROADMAP.md) prior to this session; it was added by the discovery pass, and ratified — consistent with the roadmap's standing TODO that phase relationships are the Lead Architect's inference until confirmed — as gate 1 of the three in [`IMPLEMENT.md`](IMPLEMENT.md).

## Milestones

Six. Each completion is a checkpoint trigger per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1. This phase also expects intra-milestone checkpoints on the 10–12 task threshold.

- [x] **Milestone 0 — Baseline and foundation defects** (T0, T0.5, T0.6) — **complete 2026-08-06.** Pre-phase baseline captured; both runtime-verified defects fixed and verified (font now resolves to Geist; `/system/status` reachable in dev, production gap tracked separately); 18-image canonical reference set captured on a seeded, isolated instance. Full record in [`CURRENT_STATE.md`](CURRENT_STATE.md).
- [x] **Milestone 1 — Foundation** (T1–T8) — **complete 2026-08-06.** Tokens, shell, navigation, palette, primitives, shared components, data-surface components, feedback system.
- [x] **Milestone 2 — Primary surfaces** (T9–T13) — **complete 2026-08-06.** Workbench, Secrets, Knowledge Hub, Documents, Search.
- [x] **Milestone 3 — Secondary surfaces** (T14–T22) — **complete 2026-08-06.** Notes, Projects, Prompt Studio, Model Playground, Converter, Developer Toolkit, Project Init, Settings, auth screens.
- [x] **Milestone 4 — Consolidation** (T23–T25) — **complete 2026-08-06.** Destructive-action uniformity, state-coverage sweep, dead-code removal.
- [x] **Milestone 5 — Validation** (T26–T30) — **complete 2026-08-07.** Responsive, accessibility, regression, documentation, design review. RC verified 2026-08-07.

## Risks

Full register with likelihood/impact in [`00_AUDIT.md`](00_AUDIT.md) §9. The three that most shape the plan:

- **A single global CSS change touches all 40 primitives at once** (R1). This is why T1 is isolated, sequenced first, and verified before any screen work — and why every existing shadcn token name is preserved verbatim rather than renamed.
- **Deep-link contracts break silently during page rewrites** (R2). Nine parameter contracts across seven routes, plus five compatibility redirects, have no automated coverage. Enumerated in `08_ACCEPTANCE.md` and re-tested wholesale in T28.
- **No frontend test framework exists** (R6). Regression safety rests on typecheck, lint, build, and disciplined manual verification. This is a pre-existing condition, and pretending otherwise would be the larger risk.

## Definition of Complete

- [x] All deliverables above shipped and meeting [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) fully checked off, each criterion with cited evidence — including partial-coverage findings recorded honestly rather than marked done.
- [x] Every route resolves; all five compatibility redirects land correctly; all nine deep-link contracts behave identically to the pre-phase baseline. Re-verified at final RC check, 2026-08-07.
- [x] `npx tsc --noEmit`, `npm run lint`, `npm run build` all pass; backend test suite unchanged and green (100% pass, re-run in full at RC, not just diffed).
- [x] A `/design-review` pass run against the design brief at all four breakpoints in both themes, with findings resolved or explicitly deferred. One systemic Must Fix found and fixed; two Should Fix items explicitly deferred to owner decision — see [`.design/frontend-reimagine/DESIGN_REVIEW.md`](../../../.design/frontend-reimagine/DESIGN_REVIEW.md).
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items beyond the owner-sign-off gate itself.
- [x] No unexplained dead code, no parallel frontend architecture, and no stale Phase 09 scaffold content anywhere in this directory. One stray root-level scratch file (`HANDOUT.md`, a superseded session handoff) and one missing `.gitignore` entry (`backend/.dev-data-phase09/`) found and cleaned up during RC verification.

## Cross-references

- [00_AUDIT.md](00_AUDIT.md) — the evidence base for everything above
- [CURRENT_STATE.md](CURRENT_STATE.md) · [01_SPEC.md](01_SPEC.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md) · [IMPLEMENT.md](IMPLEMENT.md)
- [`.design/frontend-reimagine/`](../../../.design/frontend-reimagine/DESIGN_BRIEF.md) — designer-skills artifacts
- [../../02_ROADMAP.md](../../02_ROADMAP.md) · [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md) · [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md)
