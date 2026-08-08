# Frontend Reimagine — Testing

> **Purpose:** How Phase 09's work is verified, given the repository's actual testing capability.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved 2026-08-06; executed throughout implementation and RC verification (2026-08-07) — see [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) for outcomes.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [01_SPEC.md](01_SPEC.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md)

---

## 1. The honest starting position

**Forge has no frontend test framework.** No Jest, no Vitest, no Playwright, no Testing Library, no `*.test.tsx` anywhere. This is a real, pre-existing gap — confirmed by direct inspection, not assumed — and it is the single largest risk in this phase ([`00_AUDIT.md`](00_AUDIT.md) §9, R6), because Phase 09 touches every frontend surface.

Introducing a test framework is **out of scope** ([`01_SPEC.md`](01_SPEC.md) §5). Doing it properly means choosing a runner, wiring it to Next 15 + React 19 + Turbopack, building a mocking layer for TanStack Query and the API client, and backfilling coverage across 17 routes — a phase-sized effort that would displace the objective this phase actually exists to serve. Doing it improperly would produce a handful of shallow tests that create false confidence.

The gap is therefore **compensated, not hidden**. What follows is what genuinely can be verified here, stated without overclaiming.

## 2. Automated verification (runs at every checkpoint, not just phase end)

| Check | Command | Gate |
|---|---|---|
| Types | `npx tsc --noEmit` | Zero errors. **Baseline captured 2026-08-06: clean.** |
| Lint | `npm run lint` | Zero errors. |
| Build | `npm run build` | Succeeds; all 17 routes compile. |
| Backend suite | `pytest` in `backend/` | Green **and unchanged**. A modified backend test means backend behavior changed — out of contract ([`03_BACKEND.md`](03_BACKEND.md) §4). |

### 2.1 Operational note — do not run `npm run build` while the dev server is live

Discovered during T0.5 execution. `next build` and `next dev --turbopack` share `frontend/.next`, and on Windows the build clobbers the running dev server's state, producing a cascade of `ENOENT: … _buildManifest.js.tmp.*` errors and a hard 500 on every route. It looks exactly like a code regression and is not one.

This phase runs the build gate at **every checkpoint**, so it will recur. Either stop the dev server before building, or expect to recover with:

```bash
rm -rf frontend/.next && npm run dev
```

### 2.2 Authenticated verification requires a human

Every `(app)` route sits behind `AuthGate`, so screenshots and deep-link checks need an unlocked session. An automated session cannot supply the master password — that is a hard constraint, not a tooling gap. The project owner unlocks the local instance in the browser once; the session cookie then persists and the rest of the run proceeds unattended.

## 3. Runtime verification

Some of this phase's most important claims are objectively measurable in a running browser, and must be measured rather than eyeballed. The discovery session already established the precedent by catching two defects this way.

| Assertion | Method | Baseline (2026-08-06, pre-phase) |
|---|---|---|
| Fonts resolve | Computed `font-family` on `<html>`/`<body>`; `--font-sans`/`--font-mono` non-empty | ❌ `"Times New Roman"`, both variables **EMPTY** |
| `/system/status` reachable | `fetch('/system/status')` status + content-type | ❌ `404`, `text/html` |
| Contrast pairs meet AA | Computed colour pairs measured against the budget in `DESIGN_TOKENS.css`, **both themes** | Never measured — no standard existed |
| Reduced motion honoured | Emulate `prefers-reduced-motion: reduce`; transition durations collapse | ❌ Zero occurrences in codebase |
| Routes resolve | Navigate all 17; expect 200 and no console error | To capture pre-phase |
| Redirects land | Request all 5 compatibility redirects; assert final URL | To capture pre-phase |
| Deep links behave | Exercise every `?open=`, `?tab=`, `?q=`, `?project_id=`, `?new=` contract in [`06_API.md`](06_API.md) §3.1 | To capture pre-phase |

> **T0 prerequisite.** Before T1 changes anything, capture the pre-phase baseline for the last three rows above, plus screenshots of all 17 routes at 375/768/1024/1440 in both themes. Without a stored baseline there is nothing to regress *against*, and with no test suite the baseline is the only regression detector this phase has.

## 4. Manual verification, per migrated screen

Every screen task carries this checklist. A screen is not done until all of it passes — visual improvement alone is explicitly not sufficient ([`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md)).

- [ ] Route resolves; no console error or warning.
- [ ] Every state reachable and correct: loading, empty, filtered-empty, populated, error, destructive.
- [ ] Every mutation still works; optimistic updates still roll back on failure.
- [ ] Every deep-link parameter behaves as it did pre-phase.
- [ ] 375 / 768 / 1024 / 1440 — behavior changes land, not just size changes.
- [ ] Both themes.
- [ ] Keyboard-only: reach every action, visible focus throughout, focus restored after overlays close.
- [ ] Icon-only controls have accessible names.
- [ ] No layout shift between skeleton and content.

## 5. Regression sweep (T28)

A full pass, not a spot check: all 17 routes, all 5 redirects, all 9 deep-link contracts, all four automated checks, both themes, all four breakpoints — compared against the T0 baseline.

## 6. Accessibility verification (T27)

Automated where possible (`axe` via browser tooling — **this would be Forge's first accessibility audit**; `04_UI_GUIDELINES.md` §4 has listed it as a TODO since the project began), manual for the rest: focus order and restoration, keyboard reachability of the Notes board and Workbench reorder, heading order, landmark structure.

**Structurally unverifiable in an automated session** — a real screen-reader pass on real assistive technology. Per [`../../13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §3 this becomes a QA ticket, explicitly tracked and explicitly non-blocking, exactly as Phase 01 established. It is not silently dropped and it is not falsely checked off.

## 7. Design verification (T30)

`/design-review` against [`DESIGN_BRIEF.md`](../../../.design/frontend-reimagine/DESIGN_BRIEF.md) at all four breakpoints in both themes, hunting specifically for the brief's anti-references: visual drift, one-off styles, excessive cards, decorative rounding, gradients, weak empty/error states, and "AI-generated UI" repetition.

## 8. Known limitations of this plan

Stated plainly so nobody mistakes coverage for proof:

- **No unit or integration tests.** Component regressions are caught by typecheck, build, and human verification — not by a suite.
- **No visual regression testing.** Screenshot comparison is manual against the T0 baseline.
- **No E2E automation.** Flow verification is manual.
- **Coverage depends on discipline.** With 17 routes and 30 tasks, the per-task checklist is the only thing preventing drift, which is why it is a gate in `IMPLEMENT.md` rather than advice here.

**Recommendation for a future phase:** introduce a frontend test framework as its own scoped phase. Phase 09's component consolidation — one `DataList` instead of seven, one `ConfirmDialog` instead of nine call sites — makes that phase substantially cheaper than it would be today.

## 9. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md) · [00_AUDIT.md](00_AUDIT.md) §9
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md) · [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md) · [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md)
