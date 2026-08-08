# Checkpoint — Frontend Reimagine (Phase 09) — 2026-08-06 (authorization)

> Trigger: **Blocking architectural decision resolved.** The [discovery checkpoint](2026-08-06-phase-09-discovery-checkpoint.md) ended with an explicit question to the project owner; this records the answer and the two revisions requested alongside it. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1 and §4.

---

## Completed Tasks

No tasks from `09_IMPLEMENTATION_TASKS.md` — T0 has not started. What completed is the authorization gate and the two revisions the owner requested at it:

- **All three authorization gates cleared**, in order and as separate acts: roadmap ratification → specification approval → implementation authorization.
- **OQ1–OQ4 resolved** in favour of the recommended answers.
- **ADR-0016 and ADR-0017 promoted** Proposed → Accepted.
- **`VERIFICATION_CONTRACT.md` written** (OQ4), scoped to the objectively checkable subset.
- **T0.5 and T0.6 added** — the two verified defects elevated into a pre-design step, with a corrected visual baseline behind it.
- **`11_SCREEN_GRAPH.md` produced** — the screen dependency graph the owner asked for before implementation.

## Modified Files

**Created**
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/11_SCREEN_GRAPH.md`
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/VERIFICATION_CONTRACT.md`
- `forge-docs/history/2026-08-06-phase-09-authorization-checkpoint.md`

**Modified**
- Phase 09: `README.md`, `00_AUDIT.md`, `01_SPEC.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`, `IMPLEMENT.md`, `CURRENT_STATE.md`
- `forge-docs/decisions/0016-*.md`, `0017-*.md` (Accepted), `decisions/README.md`
- `forge-docs/02_ROADMAP.md`, `forge-docs/implementation/README.md`

**Application code changed: none.** `git diff --stat frontend/ backend/` is still empty. The first code change of this phase will be T0.5.

## Current State

Phase 09 is **Authorized** ([`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md)) and ready to begin at T0.

### The owner's two revisions, and why both were right

**1. Elevate the font defect out of T1 and into its own pre-design step.** The original plan folded the fix into T1 (the token task). The owner's reframing is sharper: *every spacing, density, truncation, wrapping, button-sizing, and table-rhythm judgement in Forge's history was made while the application rendered in the wrong typeface.* Geist and Times New Roman have different metrics, so any design decision taken before the fix inherits the same distortion.

This produced **T0.5** (surgical fix: three lines in `globals.css`, one in `next.config.ts`, nothing else) and a consequence the revision implies but does not state — **T0.6**. T0's screenshots are in Times New Roman, so they are a record of *what shipped*, not a reference to design against. The two baselines are now stored and labelled distinctly: `baseline-as-shipped/` (historical) and `baseline-corrected/` (the reference).

**2. Add a screen dependency graph before implementation.** It changed three conclusions, which is the strongest possible argument for having asked for it:

- **It corrected the audit.** [`00_AUDIT.md`](../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md) §8 claimed features "do not import each other's internals." Mechanical extraction found **ten** cross-feature edges against a standard permitting zero — four are the intended ADR-0002 registry inversion, six are public-component reuse, and **two features reach into another feature's data layer** (`notes/note-card.tsx` → `knowledge/api`; `projects` → `model-playground` across three files including `api.ts`). The original claim is struck through in place rather than edited away.
- **It found two module cycles** — `workbench ↔ notes`, `workbench ↔ projects` — both intended, both constraining migration order. T9/T14/T15 are now an explicit cluster with mutual re-verification.
- **It found a new 🟢 defect.** Knowledge Hub routes note results to a bare `/notes` while document results get `?open=<id>` — dropping the user on an infinite board with no indication which note they clicked. The palette and `/search` both deep-link notes correctly via the same working contract. Folded into T11 as AC54.

It also raised T28's regression surface from 17 routes to **48 navigation edges**. Route-level testing would have covered 17 and missed the 31 contextual paths most likely to break during a redesign.

## Remaining Work

**Milestone 0 — T0 → T0.5 → T0.6**, then Milestones 1–5 (T1–T30). Six milestones, 33 tasks.

## Recommended Next Prompt

> Read `forge-docs/implementation/Phase-09-Frontend-Reimagine/IMPLEMENT.md`, `CURRENT_STATE.md`, and `11_SCREEN_GRAPH.md` §6–§7. Phase 09 is Authorized. Execute **Milestone 0 only — T0, T0.5, T0.6** — then stop and checkpoint. T0: capture the pre-phase baseline per `07_TESTING.md` §3, exercising all 48 navigation edges from their real source screens, plus screenshots of all 17 routes at 375/768/1024/1440 in both themes into `baseline-as-shipped/`. T0.5: fix the two verified defects only — bind `--font-sans`/`--font-mono` at `:root` outside `@theme inline`, and add the `/system/status` rewrite to `next.config.ts`; check `docker/nginx.conf` and raise a finding if production does not already route it. Change nothing else. T0.6: re-shoot the visual baseline into `baseline-corrected/`. Do not start T1.

## Known Risks

Carried forward from the discovery checkpoint, plus what authorization changed:

1. **Two features reach into other features' data layers** (new, from the graph). Architectural debt, explicitly **out of scope** — AC55 requires only that the count not increase. Fixing it means relaxing [`../07_CODING_STANDARDS.md`](../07_CODING_STANDARDS.md)'s zero-tolerance rule or adding a shared layer; both are owner decisions, and neither is presentation work. **Flagged as a candidate for its own future phase.**
2. **No frontend test framework.** Unchanged and still the largest risk. The graph improves the mitigation — 48 edges is a far better regression surface than 17 routes — but this remains compensation, not coverage.
3. **T0.5 is now the first code change** and touches `globals.css`, which all 40 primitives depend on. It is deliberately minimal for exactly this reason: bind two variables, add one rewrite, change nothing else.
4. **T1 remains the highest-risk task** — the full global CSS change. Still isolated and verified before any screen work.
5. **`docker/nginx.conf` is still unchecked** for `/system/status` routing. Now checked at T0.5b rather than T13.
6. **Scope creep**, **half-migration**, and the **nav → workbench-catalog seam** — all unchanged from the discovery checkpoint.

## Blocking decisions requiring approval

**None.** The two ADRs that were Proposed at the discovery checkpoint are now Accepted, and OQ1–OQ4 are resolved. Phase 09 has no outstanding decision blocking T0.
