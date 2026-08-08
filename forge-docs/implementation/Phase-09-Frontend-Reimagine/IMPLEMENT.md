# Frontend Reimagine — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md).
> **Ownership:** TODO — assign a phase owner.
> **Status:** ✅ **Approved to begin — 2026-08-06.** All three gates cleared, in order, in the project owner's discovery-checkpoint review. They are recorded separately because they are distinct acts and a future phase should not treat any one as implying the next:
>
> 1. **Roadmap ratification (2026-08-06)** — Phase 09's row in [`../../02_ROADMAP.md`](../../02_ROADMAP.md) §3 ratified. The phase did not exist in the roadmap before the discovery session.
> 2. **Specification approval (2026-08-06)** — this document set approved, with OQ1–OQ4 resolved in favour of the recommended answers ([`01_SPEC.md`](01_SPEC.md) §7). Two revisions were requested and applied the same day: the foundation defects were elevated into their own pre-design step (**T0.5**), and a screen dependency graph was added as a required pre-implementation artifact ([`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md)).
> 3. **Implementation authorization (2026-08-06)** — granted explicitly, as a separate act following the owner's review.
>
> Per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), the phase moved **Specification → Authorized** on 2026-08-06, and **Authorized → Implementation → Release Candidate** as of 2026-08-07 — all 30 tasks complete, RC verified, awaiting owner sign-off. Scope was held to the approved specification throughout — see [`README.md`](README.md) for the delivered-vs-scoped reconciliation and [`CURRENT_STATE.md`](CURRENT_STATE.md) for the full record.
>
> [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md) and [ADR-0017](../../decisions/0017-layered-design-token-architecture.md) are **Accepted** as of the same review.
> **Last Updated:** 2026-08-07

---

## Role

You are implementing the **Frontend Reimagine** phase of the Forge Development Kit, acting as the engineer of record. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Reimagine the presentation layer of the Forge frontend in place — one visual language, one information architecture, one application shell — while preserving every route, contract, flow, and capability exactly. See [`01_SPEC.md`](01_SPEC.md).

This phase is shaped unlike any before it: **it touches every frontend surface and no backend surface.** Prior phases added a feature; this one changes how all of them look without changing what any of them do.

## Read order for a session working this phase

1. [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md)
2. [`../../02_ROADMAP.md`](../../02_ROADMAP.md) — confirm Phase 09 is ratified and active
3. [`README.md`](README.md) and [`CURRENT_STATE.md`](CURRENT_STATE.md)
4. **This document**
5. [`00_AUDIT.md`](00_AUDIT.md) — the evidence base; do not re-derive it
6. [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) — the navigation and feature topology. **Read §6 before migrating any screen**; it names which screens are coupled and what must be re-verified after touching each.
7. [`01_SPEC.md`](01_SPEC.md), [`02_UI.md`](02_UI.md), [`05_COMPONENTS.md`](05_COMPONENTS.md) for the task at hand
8. [`../../15_VERIFICATION_FRAMEWORK.md`](../../15_VERIFICATION_FRAMEWORK.md) if closing the phase out

## Execution Rules

- [x] **Do not begin any task until this document's Status line reads "Approved to begin."** **Satisfied 2026-08-06** — all three gates cleared, in order, as separate acts.
- [ ] **T0.5 lands before any design work, and is verified before T1.** The font defect distorted every sizing, density, and truncation judgement in the product's history; the redesign's decisions must be made against correct type metrics. T0.5 is deliberately surgical — three lines in `globals.css`, one in `next.config.ts`, nothing else. **T0.6 then re-shoots the visual baseline**, because T0's screenshots are in Times New Roman and are a historical record, not a reference to design against.
- [ ] **Scope is locked** to [`01_SPEC.md`](01_SPEC.md)'s fifteen functional requirements. Nothing in §5's out-of-scope list may be touched. Anything discovered there becomes a **finding in `CURRENT_STATE.md` → Known Issues**, never an in-flight edit.
- [ ] **Preservation is the primary obligation, not the redesign.** Every task in `09_IMPLEMENTATION_TASKS.md` carries a "Preserve" line. That line is the contract. A task whose visuals are finished but whose Preserve line is unverified is **not complete** and must not be checked off.
- [ ] **Zero backend diff.** `git diff --stat backend/` must be empty on this branch, at every commit. If a change appears to require the backend, **stop** and raise it as a blocking architectural decision with a drafted ADR ([`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §6). Do not modify backend behavior to make a frontend layout easier.
- [ ] **T1 lands and is verified alone.** It is a single global CSS change affecting all 40 primitives simultaneously. Verify computed font-family, a clean build, and five spot-checked primitives in both themes **before** starting T2. Do not batch T1 with screen work.
- [ ] **Preserve every shadcn token name verbatim.** Additions only. Renaming one is a 40-file breaking change bought for nothing.
- [ ] **Preserve every `components/ui/*` export name and prop signature.** If a retune seems to need an API change, that is a finding, not an edit.
- [ ] **`NAV_ITEMS` changes are additive only.** No `href`, `title`, `icon`, `shortcut`, or `description` value may change. After any nav change, **re-verify the Workbench pinned-tools catalog explicitly** — that manually-synced seam produced Phase 08's `BUG-0001`.
- [ ] **No parallel frontend** ([`01_SPEC.md`](01_SPEC.md) NFR3). No second shell, second router, duplicate API client, parallel page directory, or `*-v2`/`*-new` file. If a migration genuinely requires a temporary parallel implementation, document the reason **and the removal boundary at the moment it is created** — not afterwards — and remove it in Milestone 4.
- [ ] **No fake data.** Never introduce placeholder content to make a screen look complete.
- [ ] **No new dependency.** [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 requires asking first; this phase's answer is already no.
- [ ] **Frozen phases: presentation only.** Phases 01–08 are Frozen. Restyling their surfaces is in contract; changing their behavior is not. A behavior problem found inside a frozen surface is a bug report ([`../../12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md)), not an edit.
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — no cross-feature imports of internals, endpoint knowledge stays in `features/*/api.ts`, feature components stay feature-owned.
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) **as work progresses**, not only at checkpoints. This phase is long enough that reconstructing state after the fact will fail.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

**Must ask first, beyond the repo-wide triggers:**
- [ ] Any change to a route, route parameter, or redirect — even one that looks equivalent.
- [ ] Any change to an API call site, request/response handling, or a TanStack Query key.
- [ ] Removing any dependency, including `framer-motion` (OQ3).
- [ ] Any deviation from the confirmed aesthetic direction, typography decision, or IA in [`01_SPEC.md`](01_SPEC.md) §6.
- [ ] Introducing any temporary parallel implementation.

**May do without asking:**
- [ ] Implement any authorized task exactly as specified.
- [ ] Restyle within the token system.
- [ ] Extract a duplicated pattern into a component **already named** in [`05_COMPONENTS.md`](05_COMPONENTS.md) §3.2.
- [ ] Fix an accessibility defect on a surface being actively migrated.

## Quality Gates

Every task clears [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) before being marked complete, plus this phase's per-screen checklist ([`07_TESTING.md`](07_TESTING.md) §4).

A screen is complete only when **visual quality + UX quality + functionality + accessibility + regression safety** are all satisfied. Looking better is necessary and not sufficient.

`npx tsc --noEmit`, `npm run lint`, and `npm run build` pass at **every checkpoint**, not only at phase end.

## Checkpoint Rules

Per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md), exactly and without exception:

- Every milestone boundary (five in this phase).
- Every 10–12 completed tasks.
- ~70% context usage.
- Any blocking architectural decision.

Each checkpoint produces the protocol's exact seven sections, updates `CURRENT_STATE.md`'s ten sections and this phase's task checkboxes, and adds an entry under [`../../history/`](../../history/).

Given 31 tasks across 17 routes, expect **six or more** checkpoints. Do not defer one because a milestone is nearly finished.

## The specific ways this phase can go wrong

Named explicitly so a future session recognises them in the moment:

1. **Silent contract breakage.** A page is rewritten cleanly and a `?open=` handler quietly disappears with it. Nothing fails to compile. Nothing errors. It is simply gone. → This is why every task has a Preserve line and why T0 captures a baseline first.
2. **Token drift.** A screen "just needs" one arbitrary value, then another, and by Milestone 3 there is no system. → Zero arbitrary Tailwind values (AC4). If a value is missing from the ramp, add it to the ramp.
3. **The Swiss/Rams seam spreading.** Swiss is exactly three typographic utilities applied inside Rams containers. If it starts making container, spacing, or colour decisions, there are now two design systems.
4. **Scope creep from proximity.** Touching all 17 routes means encountering every known gap in the product. Pagination, test coverage, and backend inconsistencies are all out of scope **while you are looking directly at them.**
5. **Half-migration.** Stopping mid-phase leaves Forge visibly two-toned — the exact failure this phase exists to eliminate. If the phase must pause, pause at a **milestone boundary**, never mid-milestone.

## Cross-references

- [README.md](README.md) · [00_AUDIT.md](00_AUDIT.md) · [01_SPEC.md](01_SPEC.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md) · [CURRENT_STATE.md](CURRENT_STATE.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md) · [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md) · [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md)
