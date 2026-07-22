# 14 — Implementation Playbook

> **Purpose:** Practical patterns and checklist for implementation sessions, distilled from Phase 01 and Phase 02 execution. This is a living document that grows with each completed phase.
> **Scope:** Implementation workflow, not architecture or product decisions (see [`03_ARCHITECTURE.md`](03_ARCHITECTURE.md) and [`01_PRODUCT_PRINCIPLES.md`](01_PRODUCT_PRINCIPLES.md)).
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Draft — first edition, patterns from Phase 01–02.
> **Version:** 0.1.0
> **Last Updated:** 2026-07-22
> **Depends On:** [`10_CHECKPOINT_PROTOCOL.md`](10_CHECKPOINT_PROTOCOL.md), [`12_BUG_CLASSIFICATION.md`](12_BUG_CLASSIFICATION.md), [`13_PHASE_LIFECYCLE.md`](13_PHASE_LIFECYCLE.md)

---

## 1. Pre-Implementation Checklist

- [ ] **Read the governance stack first.** Before writing code, read [`03_ARCHITECTURE.md`](03_ARCHITECTURE.md), [`01_PRODUCT_PRINCIPLES.md`](01_PRODUCT_PRINCIPLES.md), [`07_CODING_STANDARDS.md`](07_CODING_STANDARDS.md), [`04_UI_GUIDELINES.md`](04_UI_GUIDELINES.md), any active ADRs, and the current phase's own spec package (if one exists).
- [ ] **Verify scope authorization.** If the phase spec doesn't exist or you're unsure about scope, ask the project owner or write a draft spec and present it for explicit sign-off before implementing. Don't guess at scope — a wrong guess costs more than a conversation.
- [ ] **Check for prior art.** Search the codebase for similar patterns. Use `codegraph_search` or `Grep` to find how other features handle the same problems (e.g., "how do we delete with activity logging?" — find an existing service that does it, copy the pattern, don't invent).
- [ ] **Establish the checkpoint cadence.** Phase 01 and 02 both used roughly 10–14 tasks grouped into 2–3 milestones. Estimate task count; if it exceeds ~20 for a single session, consider splitting across sessions.

## 2. Specification-First Workflow

- [ ] **Write the spec before code.** Not a placeholder — a complete, filled-in spec package: 01_SPEC.md (complete summary), 02_UI.md (all screens and states), 03_BACKEND.md (service design), 04_DATABASE.md (schema), 05_COMPONENTS.md (component breakdown), 06_API.md (endpoint contracts), 07_TESTING.md (test plan), 08_ACCEPTANCE.md (pass/fail criteria), 09_IMPLEMENTATION_TASKS.md (ordered task list), 10_RELEASE_NOTES.md (user-facing summary).
- [ ] **Get explicit buy-in on scope decisions.** If the spec defers anything to "future phases," call that out explicitly. If you're making architectural trade-offs (e.g., "no LLM calls," "download-only, no filesystem write"), document the **why** so future readers understand the boundary.
- [ ] **Lock the spec before implementation.** Use the phase's own ADR pattern or a note in the spec's header ("Accepted — no changes without explicit approval") to signal that implementation has started.
- [ ] **Update CURRENT_STATE.md at every checkpoint.** Not at the end — continuously. This is your live snapshot of where the phase actually stands; it drives the next prompt.

## 3. Architecture & Feature Isolation

- [ ] **One feature per phase, fully isolated.** New code in `backend/app/services/feature-name/`, `backend/app/models/feature-name.py`, `backend/app/schemas/feature-name.py`, `backend/app/api/routes/feature-name.py`. Frontend code in `frontend/features/feature-name/`, `frontend/app/(app)/feature-name/`. No cross-feature imports.
- [ ] **Reuse, don't modify.** If your feature needs to use ActivityLog, use the existing `backend/app/services/activity.py` unchanged. If you need nav registry, add your entry to `frontend/lib/nav-registry.ts` but don't modify its structure. This keeps regression risk low.
- [ ] **One migration per phase.** Additive only (new tables, new columns). Name it `NNNN_phase-name.py` matching the phase number. Include a guard for fresh installs (check if table exists before creating). Test it runs automatically on docker compose boot.
- [ ] **Use Pydantic schemas for all API input.** Define a schema class per input type (GenerateRequest, UpdateDocumentIn, etc.); the router always type-hints the body param with the schema. This buys you validation + documentation.

## 4. Implementation Task Workflow

- [ ] **Order tasks in dependency order.** Typical order: 1) branch, 2) model, 3) migration, 4) schemas, 5) templates/static content, 6) service layer (business logic), 7) API routes, 8) backend tests, 9) frontend API layer, 10) frontend components, 11) page/nav, 12) integration tests, 13) full stack verification, 14) final docs. Don't code frontend before the API exists — test each layer as you build it.
- [ ] **Use TaskCreate / TaskUpdate to track progress.** Mark each task in_progress when you start it, completed when it's done. This is your real-time status artifact; refer back to it in checkpoints.
- [ ] **Checkpoint every 3–5 tasks.** Don't wait until "all 14 are done" to verify anything. After task 3 (schemas ready), run a quick test of the API layer. After task 8 (tests done), make sure they actually pass. After task 11 (frontend page done), try the real app in a browser. Checkpoints catch problems early.

## 5. Testing Requirements

### Backend

- [ ] **Write tests for the service layer, not just the routes.** Service tests run against an in-memory SQLite; they're fast and prove business logic. Route tests use TestClient and prove request/response contracts.
- [ ] **Test the happy path and the edge cases.** At minimum: valid input → success, missing required field → 422, not-found ID → 404, invalid enum → 422. For more complex features, add scenarios like "update A then update A again" (idempotence), "delete then try to re-fetch" (cascades), "concurrent operations" (if applicable).
- [ ] **Verify fixtures are isolated.** Each test should start fresh — use per-test or per-module fixtures, not shared state across tests. A failing test shouldn't affect the next one.
- [ ] **Run the full test suite before declaring "tests pass."** Not just new tests: `pytest backend/tests/ -v` and check that both new and existing tests pass. If you broke anything, fix it before moving on.

### Frontend

- [ ] **Build and lint must pass.** `npm run build` and `npm run lint` clean, no errors or warnings. Type check passes: `tsc --noEmit`.
- [ ] **Manual browser verification replaces unit tests (for now).** Since there's no frontend test framework yet, test the feature in a real browser: fill the forms, submit, get error states, try edge cases, check the history list, delete things. Test in light and dark mode if there's CSS. Test on mobile (375px) if there's responsive layout.
- [ ] **Verify interaction states.** Buttons disabled when invalid? Loading spinner appears? Errors clear when fixed? Toasts pop up? Don't just check "the page renders."

### Integration

- [ ] **Run `docker compose build` and `docker compose up` for a full-stack test.** Both images build, migrations apply, app boots. The real app works through the nginx proxy. This is your only way to catch environment/config issues before release.
- [ ] **Test the real feature end-to-end in the running app.** Not just the API or frontend alone — use the actual UI, see the actual data flow, verify it appears in Activity logs if applicable. This is your last chance to catch integration bugs.

## 6. Bug Classification & Release Candidate

- [ ] **Run an independent audit before signing off.** This is the Release Candidate phase. Have fresh eyes (or a separate pass by the same engineer) review the implementation against the spec. Look for:
  - Acceptance criteria actually met (not just "looks good")
  - Scope creep (did we build something not in the spec?)
  - Regressions (did we break existing features?)
  - Missing error handling (what happens when the database is slow? when a file is missing?)
- [ ] **Classify all findings per [`12_BUG_CLASSIFICATION.md`](12_BUG_CLASSIFICATION.md).** Is it a BLOCKER (data loss, security, build failure, acceptance failure)? MAJOR (UX inconsistency, confirmed a11y gap, perf regression)? MINOR (cosmetic, cleanup, refactoring, nice-to-have)? Unverified (tested with environment constraints — keyboard nav without a real input device)?
- [ ] **Fix all BLOCKERs before merge.** MAJORs and MINORs go to the project owner to decide: fix before merge, fix in a fast-follow, or accept and backlog. Don't expand the phase scope by fixing every MINOR; file them and move on.
- [ ] **Document known limitations honestly.** If keyboard navigation wasn't tested because the environment doesn't support it, say so. File a QA ticket for post-implementation verification, don't hide it.

## 7. Checkpoint Cadence

**Checkpoint Pattern:** After milestones (typically every 3–5 tasks, not every single task).

Each checkpoint:
- [ ] Run tests; confirm they pass.
- [ ] Update CURRENT_STATE.md with what's done, what's in progress, what's next.
- [ ] If you found and fixed bugs during implementation, document them in a `BUGS/` folder under the phase.
- [ ] If something's stuck or uncertain, escalate to the project owner (ask, don't guess).
- [ ] Use the checkpoint as a natural point to break the session if you need to. The next session resumes from the checkpoint, not from the beginning.

**Example:** Phase 02 had 14 tasks across 3 milestones:
- Milestone 1 (T1–T9): Backend engine. Checkpoint after T9: backend tests pass, API verified via curl/TestClient.
- Milestone 2 (T10–T12): Frontend UI. Checkpoint after T12: frontend build/lint pass, components render, browser test forms.
- Milestone 3 (T13–T14): Full validation + docs. Checkpoint after T14: docker compose passes, RC audit done, specs updated, ready for sign-off.

## 8. Documentation Requirements

### Per-Phase Docs

- [ ] **01_SPEC.md:** Complete, locked, no TODOs (except forward-looking "get retroactive sign-off").
- [ ] **02_UI.md through 08_ACCEPTANCE.md:** All filled in, not placeholders. These are the acceptance criteria; they must be verifiable.
- [ ] **09_IMPLEMENTATION_TASKS.md:** Ordered task list with owner, status, completion % at each checkpoint.
- [ ] **10_RELEASE_NOTES.md:** User-facing summary (what's new, not what you built). Short, action-oriented.
- [ ] **README.md:** Phase overview, definition of "complete," key dates.
- [ ] **CURRENT_STATE.md:** Live snapshot; updated at every checkpoint, never left stale. This is where you record what actually happened vs. what was planned.
- [ ] **IMPLEMENT.md:** Execution contract — how the implementation will be run (if it's complex). For most features, this is very short or empty.

### Root-Level Docs

- [ ] **Update [`02_ROADMAP.md`](02_ROADMAP.md) after sign-off.** Move this phase to "Complete," update Phase 03 (or next phase) status, estimate dates for upcoming work.
- [ ] **Add a checkpoint entry to [`history/`](history/).** File named `YYYY-MM-DD-phase-NN-final-checkpoint.md` with: what was built, key decisions, bugs found and fixed, known limitations, readiness for the next phase.
- [ ] **Link between related docs.** Use cross-references (Section `X` in file `Y`); make it easy to trace from spec → implementation → acceptance → release notes.

## 9. Common Implementation Pitfalls (Avoid)

1. **Skipping the spec.** "I'll figure it out as I code" → scope creep, rework, missed acceptance criteria. Always spec first.
2. **Modifying existing code unnecessarily.** "I need to refactor ActivityLog while I'm at it" → regression risk, scope creep. Reuse, don't rewrite.
3. **Testing only the happy path.** "It works when I use it correctly" → surprises in production. Test errors, edge cases, concurrent access.
4. **Leaving known issues unfiled.** "We'll fix it later" → it doesn't get fixed; it festers. File tickets (MINOR, QA, or BLOCKER), don't ignore them.
5. **Deferring the browser test.** "The tests pass, so it works" → UI is broken, the form doesn't actually submit. Test in a real browser before declaring done.
6. **Cargo-culting patterns without understanding them.** "I'll use react-hook-form because the README says it's installed" → you introduce a new pattern nobody else uses. Stick to the existing convention even if it's less elegant.
7. **Writing huge commits.** One feature per commit is good; one 50-file, 3000-line commit is hard to review and rollback. Keep commits scoped and reviewable.
8. **Not running the full test suite.** "My tests pass" — did the existing tests still pass? Run `pytest backend/tests/ -v` and `npm run build && npm run lint` before you call it done.

## 10. Definition of "Production-Ready"

A feature is production-ready when **all** of these are true:

- [ ] Spec is complete, locked, and accepted.
- [ ] All acceptance criteria in 08_ACCEPTANCE.md are verified (or honestly marked unverifiable + filed as QA tickets).
- [ ] Independent Release Candidate audit is done; zero BLOCKERs remain.
- [ ] Backend and frontend build/test suites pass.
- [ ] `docker compose build` and full-stack boot succeed.
- [ ] Feature is manually verified in the real running app (not just unit tests).
- [ ] No regressions in existing features (spot-check a few existing tools).
- [ ] Activity logging (if applicable) works and shows up in Activity history.
- [ ] All known limitations are documented and classified (BLOCKER, MAJOR, MINOR, QA).
- [ ] Project owner has signed off (or self-authorized per explicit instruction, with retroactive sign-off a TODO).
- [ ] A checkpoint document exists recording what was built, decisions made, and readiness for the next phase.

If any one of these is false, the feature is not ready to merge.

## 11. The Release Ceremony

Once a phase passes RC and gets owner sign-off:

1. [ ] **Tag the release:** `git tag v0.N.0-phase-slug` (e.g., `v0.2.0-project-init`).
2. [ ] **Merge to `master`:** `git checkout master && git merge --no-ff Phase-NN-Name` (preserves branch history).
3. [ ] **Freeze the implementation directory.** Phase 02 folder goes read-for-bugfixes-only; new features for Phase 03 go to a new `Phase-03-` folder.
4. [ ] **Update roadmap and close the phase.** [`02_ROADMAP.md`](02_ROADMAP.md): mark this phase Complete, estimate dates for Phase 03, adjust future phases if needed.
5. [ ] **Archive the phase's temporary files.** QA tickets, BUGS/ folder, checkpoint documents → [`history/Phase-NN/`](history/) folder for posterity.

## 12. Tools & Environment

### Must-Have

- Git (version control, history, branches)
- Docker (reproducible builds, full-stack testing)
- Backend test framework: pytest (sync and async tests)
- Frontend type checker: TypeScript (`tsc --noEmit`)
- Frontend linter: ESLint + Prettier

### Nice-to-Have (Add if Available)

- Frontend unit test framework (Vitest, Jest) — Phase 01 shipped without one; Phase 02 relied on manual browser tests. Not a blocker, but would improve test coverage.
- API documentation generator (Swagger/OpenAPI) — FastAPI + Pydantic auto-generates it; nice for keeping docs fresh.
- Performance profiler — for catching regressions in hot paths.

### What We Don't Use (Keep It Simple)

- GraphQL (overkill for this scope; REST is fine)
- Monorepo tools (we have one small monorepo; Nx/Turborepo would be overhead)
- API mocking libraries (test against the real API)
- Stub/mock database (use real SQLite in tests, not mocks that diverge from prod)

## 13. Cross-References

- [`10_CHECKPOINT_PROTOCOL.md`](10_CHECKPOINT_PROTOCOL.md) — how to structure checkpoints
- [`12_BUG_CLASSIFICATION.md`](12_BUG_CLASSIFICATION.md) — BLOCKER vs. MAJOR vs. MINOR
- [`13_PHASE_LIFECYCLE.md`](13_PHASE_LIFECYCLE.md) — full phase lifecycle (Spec → Implement → RC → Sign-off → Release → Freeze)
- [`07_CODING_STANDARDS.md`](07_CODING_STANDARDS.md) — code style, naming, documentation-in-code
- [`03_ARCHITECTURE.md`](03_ARCHITECTURE.md) — invariants (thin routers, feature isolation, no cross-imports)
- [`01_PRODUCT_PRINCIPLES.md`](01_PRODUCT_PRINCIPLES.md) — design principles
- [Phase 01 history](history/Phase-01-Workbench/) — lessons learned, bugs found, decisions made
- [Phase 02 history](history/2026-07-22-phase-02-final-checkpoint.md) — checkpoint entry for reference

## 14. TODO

- [ ] Expand this playbook with patterns from Phase 03 and beyond as they complete.
- [ ] Add a "Performance Optimization Checklist" once we have measured bottlenecks.
- [ ] Add a "Accessibility Audit Checklist" once we have real screen-reader testing.
- [ ] Formalize the "design review" step (currently informal); add mockup approval checkpoint if designs become complex.

---

**This is a living document.** Each phase will refine these patterns. If a future phase discovers a better way to do something, update this playbook so the next phase benefits from it.
