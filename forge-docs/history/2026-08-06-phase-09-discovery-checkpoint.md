# Checkpoint — Frontend Reimagine (Phase 09) — 2026-08-06

> Trigger: **Milestone completion** (discovery/design pass) **and blocking architectural decision** — two ADRs drafted and three authorization gates outstanding. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1.

---

## Completed Tasks

No tasks from `09_IMPLEMENTATION_TASKS.md` — that document was *produced* by this session, and T0–T30 are all unstarted and unauthorized. What completed is the discovery and design pass the phase brief required before any implementation task exists:

- Full frontend codebase audit — 17 routes, 40 primitives, 18 feature folders, 8 shared components read directly; 112 backend endpoints enumerated across 18 modules.
- Runtime verification in a live browser, which found two real defects (below).
- `julianoczkowski/designer-skills` installed (8 skills) and relocated to `.claude/skills/` at the repo root.
- Designer-skills workflow executed: `grill-me` → `design-brief` → `information-architecture` → `design-tokens` → `brief-to-tasks`.
- Four blocking design decisions put to the project owner and confirmed.
- One proposed IA change verified and **rejected on evidence** before it reached the specification.
- Complete Phase 09 document set (14 documents), two ADRs, roadmap entry.

## Modified Files

**Created — designer-skills artifacts**
- `.design/frontend-reimagine/DESIGN_BRIEF.md`
- `.design/frontend-reimagine/INFORMATION_ARCHITECTURE.md`
- `.design/frontend-reimagine/DESIGN_TOKENS.css`
- `.design/frontend-reimagine/TASKS.md`

**Created — Phase 09 documentation** (`forge-docs/implementation/Phase-09-Frontend-Reimagine/`)
- `README.md`, `00_AUDIT.md`, `01_SPEC.md`, `02_UI.md`, `03_BACKEND.md`, `04_DATABASE.md`, `05_COMPONENTS.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`, `10_RELEASE_NOTES.md`, `IMPLEMENT.md`, `CURRENT_STATE.md`

**Created — decisions**
- `forge-docs/decisions/0016-grouped-navigation-and-search-surface-consolidation.md` (Proposed)
- `forge-docs/decisions/0017-layered-design-token-architecture.md` (Proposed)

**Created — tooling**
- `.claude/skills/` — 8 designer skills

**Modified**
- `forge-docs/02_ROADMAP.md` — Phase 09 row added to §3; blocking ratification TODO added to §6
- `forge-docs/decisions/README.md` — ADR-0016/0017 indexed; TODO added

**Application code changed: none.** `git diff --stat frontend/ backend/` is empty.

## Current State

Phase 09 exists, is fully specified, and is **not authorized**. It sits at **Specification** in [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md).

The phase did not exist at session start: there was no `Phase-09-*` folder anywhere in the repository and no Phase 09 row in the roadmap. The brief referred to an "uploaded `Phase-09-Frontend-Reimagine/` folder" as the phase's documentation home; no such folder was present. It was scaffolded from the conventions of Phases 07–08.

**Two defects were verified at runtime, not inferred:**

1. 🔴 **The entire application renders in Times New Roman.** `app/globals.css:11` declares `--font-sans: var(--font-sans)` inside `@theme inline` — a self-reference that resolves empty, making `html { @apply font-sans }` an invalid declaration. Geist is downloaded on every page load and never applied. `--font-mono` fails independently (`next/font` scopes it to the `<body>` class, unreachable from an `@theme inline` reference at `:root`). Measured on `/unlock`: computed `font-family` `"Times New Roman"` on both `<html>` and `<body>`; `--font-sans` and `--font-mono` both empty; `--font-geist-sans` correctly populated.

2. 🟡 **`/system/status` 404s.** The backend serves it (`health.py:23`, mounted at root); `next.config.ts` proxies only `/api/*` and `/health`. The Settings About card's Storage line has therefore never rendered. Measured: `404`, `content-type: text/html`. Fixable with one frontend rewrite — no backend change.

**Design direction confirmed by the project owner:** Dieter Rams functionalist base with Swiss typographic treatment on data surfaces; wire up the already-bundled Geist rather than introducing a new face; group the sidebar and resolve the search-surface overlap; migrate all 17 routes in this phase.

**Type baseline captured: `npx tsc --noEmit` is clean.**

## Remaining Work

Three authorization gates, in order, each a distinct act:

1. **Roadmap ratification** — Phase 09's row awaits owner confirmation (`02_ROADMAP.md` §6).
2. **Specification approval** — including OQ1–OQ4 in `01_SPEC.md` §7 (`table` primitive adoption, `framer-motion` removal, verification-contract shape).
3. **Implementation authorization** — separate from specification approval, as in every prior Forge phase.

Then T0 (baseline capture) → T1–T30 across five milestones.

## Recommended Next Prompt

> Read `forge-docs/implementation/Phase-09-Frontend-Reimagine/IMPLEMENT.md` and `CURRENT_STATE.md`. The project owner has ratified Phase 09 in the roadmap, approved the specification, resolved OQ1–OQ4, and granted implementation authorization. Update `IMPLEMENT.md`'s Status line to "Approved to begin", then execute **T0 only** — capture the full pre-phase baseline per `07_TESTING.md` §3 (all 17 routes at 375/768/1024/1440 in both themes, all 5 redirects, all 9 deep-link contracts, tsc/lint/build output). Do not start T1 until the T0 baseline is stored and I have confirmed it.

## Known Risks

1. **A recommendation I made was wrong, and verification caught it.** The IA question offered "retire `/search` — Knowledge Hub already supersedes it" as the recommended option, and the owner selected it. Checking the two services before writing it into the IA showed `/api/search` covers secrets + notes + documents while `/api/knowledge` covers notes + documents only (ADR-0015 — no secrets path at all). Implementing the proposal as stated would have silently removed secret search. Corrected across the IA, spec, audit, and ADR-0016 §3.1, and reported to the owner rather than quietly changed. **The generalizable risk: a consolidation that looks like simplification but narrows capability.** ADR-0016 §3.1 records it specifically so the idea is not re-proposed on the same false premise.

2. **No frontend test framework exists.** No Jest, Vitest, Playwright, or Testing Library; zero test files. This is the phase's largest risk, since it touches all 17 routes. Out of scope to fix here. Compensated by the T0 baseline, per-task Preserve contracts, and the T28 regression sweep — but this is mitigation, not coverage, and `07_TESTING.md` §8 says so plainly.

3. **T1 is a single global CSS change affecting all 40 primitives simultaneously.** Sequenced first and alone, verified before any screen work.

4. **The nav → workbench-catalog seam is manually synced** and produced Phase 08's `BUG-0001`. Grouping the sidebar touches `NAV_ITEMS`. Mitigated by making the change additive and by an explicit re-verification criterion (AC16).

5. **Scope creep risk is unusually high.** Touching every route means encountering every known gap in the product — pagination, test coverage, backend inconsistencies — while looking directly at them. `IMPLEMENT.md` names this as a specific failure mode.

6. **A half-migration is worse than none.** If the phase pauses, it must pause at a milestone boundary, never mid-milestone.

7. **`docker/nginx.conf` has not been checked** for `/system/status` routing. If production does not already proxy it, that is a real production gap — T13 checks and raises it rather than silently patching.

## Blocking decisions requiring approval

Two ADRs are drafted and **Proposed**, per [`../09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) §6:

- [ADR-0016](../decisions/0016-grouped-navigation-and-search-surface-consolidation.md) — grouped navigation and one job per search surface. Upholds ADR-0007; supersedes nothing; changes no search scope.
- [ADR-0017](../decisions/0017-layered-design-token-architecture.md) — three-layer tokens preserving the shadcn semantic contract; records deliberate deviations from the `design-tokens` and `frontend-design` skills.

**Question for the project owner:** do you ratify Phase 09's roadmap entry, approve this specification (including the four open questions), and authorize implementation to begin at T0?
