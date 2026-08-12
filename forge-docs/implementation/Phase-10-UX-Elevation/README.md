# UX Elevation — README

> **Purpose:** Entry point for the Phase 10 UX Elevation pass — objective, scope, process note, and deliverables.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** 🔒 **Released & Frozen.** Committed to `master` at `4f58b64`, tagged `v0.10.0`, 2026-08-12. Owner authorized this release by directing the commit → tag → freeze sequence after reviewing the release-candidate report and a categorized diff audit — see §"A note on process" below for what that does and doesn't equate to. Per [`../../13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §4, this directory now accepts bug fixes only — no new features, no architectural changes; further UX work begins as a new phase. End-of-phase release notes moved to [`../../history/Phase-10/10_RELEASE_NOTES.md`](../../history/Phase-10/10_RELEASE_NOTES.md) per §5.
> **Last Updated:** 2026-08-12

---

## A note on process, read this first

Phases 01–09 in this directory were each run through this repository's full FDK phase lifecycle: a discovery pass, a written specification, an explicit roadmap-ratification and implementation-authorization gate, a `VERIFICATION_CONTRACT.md` agreed in advance, and a formal acceptance sign-off (see [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md)).

**Phase 10 did not go through that process**, and this documentation does not claim otherwise. What actually happened:

1. The project owner requested a screen-by-screen UX elevation pass directly in conversation, framed against Phase 09's own retrospective (Phase 09 fixed *system consistency* — tokens, shared components, responsive/accessibility baseline; it explicitly did not touch *screen-level information hierarchy and interaction models*).
2. A **lightweight implementation plan** was written collaboratively with the owner (three rounds of explicit review and revision) and approved via the harness's plan-mode gate — not this repository's roadmap-ratification/spec-approval/authorization three-gate sequence. That plan file is the actual planning source of truth for this phase: `C:\Users\dandr\.claude\plans\forge-screen-by-screen-ux-squishy-cocoa.md` (a session-local path, not part of this repo — its content is reproduced in [`01_SPEC.md`](01_SPEC.md) so it survives outside that session).
3. Implementation proceeded screen-by-screen against that plan, with the plan's own explicit instruction that every proposed redesign was a **hypothesis to validate against the live, running screen — not a locked spec**. Several hypotheses were confirmed as written; at least one was found wrong on inspection and discarded (see [`01_SPEC.md`](01_SPEC.md) §3).
4. A **release-readiness pass** (type-check, full-repo lint, production build, backend test suite, Docker image builds, diff-scope audit) was run afterward and is recorded in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md). This is the actual verification source of truth for this phase.
5. This documentation set — including this file — was **written after implementation and verification were complete**, to backfill the structural convention Phases 01–09 established. It does not describe a discovery/spec/authorization sequence that occurred; it describes what was actually planned, built, decided, and verified.
6. **Release.** The owner reviewed the release-candidate report and a categorized diff audit (product changes / documentation / `.gitignore` fix / Sheet-header fix, separated explicitly) directly in conversation, then instructed the commit → tag → freeze sequence. That instruction is the authorization this release rests on. It is not the same artifact as Phases 01–09's formal owner-sign-off statement ("APPROVED, Accepted for Release" against a pre-agreed acceptance document) — no such statement was sought or given for Phase 10, and this documentation does not claim one was.

If a future phase wants the full FDK ceremony applied retroactively to this work (a proper `00_AUDIT.md`, a pre-agreed `VERIFICATION_CONTRACT.md`, a ratified roadmap entry predating implementation), that is new work, not a correction of this record.

## Objective

Elevate the frontend above the system-consistency layer Phase 09 delivered — **Level 2, screen intelligence** — by re-examining each screen's information hierarchy, interaction model, and spatial composition against what the user is actually trying to do on that screen, and changing the composition where it doesn't serve that job. Explicitly *not* a second visual-polish pass: no token changes, no new shared primitives beyond what a screen's redesign genuinely required, no re-litigating Phase 09's component consolidation.

The guiding constraint, stated in the plan itself: a proposed redesign is a hypothesis to confirm, modify, or reject against the live screen — never something to implement merely because it appeared in the plan document. Restraint on a screen whose existing interaction model already fit its job was an explicit objective of this phase, not a shortfall.

## Scope

**In scope — delivered:**
- [x] **Workbench** — replaced the uniform equal-weight grid with a weighted primary/rail composition (jump-targets vs. glanceable panels), scoped drag-reorder per column, additive `column` field on the panel registry.
- [x] **Notes** — search/filter now dims non-matching notes in place on the canvas instead of swapping to a result list, preserving spatial position as information.
- [x] **Model Playground** — collapsed the always-expanded provider-setup panel into a one-line summary so the run/comparison workspace gets primary vertical space; confirmed the side-by-side comparison grid already existed (a proposed-primitive hypothesis correctly discarded on inspection).
- [x] **Prompt Studio** — reordered composition so the body editor is the persistent primary surface; Variables/Preview moved from always-stacked panels into a tab strip below the body.
- [x] **Knowledge** — result list now groups by type (Documents/Notes) with section headers when both types are present in an unfiltered result set.
- [x] **Projects** — cards distinguish empty vs. active projects, show recency; Project Detail's scoped lists (secrets/notes/documents) now deep-link to the actual item instead of rendering as inert rows.
- [x] **Documents** — mobile empty-state copy corrected (previously referenced a sidebar "on the left" that doesn't exist once the list is behind a drawer trigger below `lg`).
- [x] **Cross-cutting bug fix, found during final audit, not scoped in the original plan:** `SheetContent`'s built-in absolute-positioned close button collided with custom header action icons on two screens (Secrets detail sheet, Ingest preview sheet). Both fixed; all other `Sheet`/`Dialog` consumers audited and confirmed unaffected.

**Verified and intentionally left unchanged** — restraint was the correct call, not incomplete work:
- [x] **Secrets** — already the Phase 09 reference data-surface pattern; treated as the pattern other screens borrow from, not a redesign target.
- [x] **Search** — already the correct list-of-results model; its one real gap (weak discoverability) is a navigation question tracked in ADR-0016, not a Phase 10 layout problem.
- [x] **Converters, Developer Toolkit** — already dense, scannable technical-instrument grids; matched their target model on inspection.
- [x] **Settings** — already correctly grouped into reference vs. consequential sections (Phase 09 T21 work); held up under this pass's own bar.
- [x] **Project Init** — already a clear single-focus template picker.
- [x] **Unlock, Setup** — already correctly minimal single-focus security gates; decorating them would have violated this phase's own restraint principle.

**Out of scope — held throughout:**
- [x] Any backend change — `git diff --stat backend/ docker/` empty (verified at RC).
- [x] Any new product capability, API contract change, or data-model change.
- [x] Phase 09's design tokens, shared component library, or responsive/accessibility baseline — reused, not reopened.
- [x] The deliberate prior decision documented in Phase 09 T16 (Prompt Studio does not use `FilterRail` — list-XOR-detail pattern doesn't fit that component's mobile-drawer contract) — re-validated against this phase's own bar and preserved, not overridden.

## Relationship to the shipped application

Touches 8 of 17 frontend routes' feature code (Workbench, Notes, Model Playground, Prompt Studio, Knowledge, Projects + Project Detail, Documents) plus two shared-component consumers found during final audit (Secrets detail sheet, Ingest preview sheet). Touches **no** backend surface.

- Related frontend: `frontend/features/workbench/`, `frontend/features/notes/`, `frontend/features/model-playground/`, `frontend/features/prompt-studio/`, `frontend/features/knowledge/`, `frontend/features/projects/`, `frontend/app/(app)/documents/`, `frontend/features/secrets/secret-detail-sheet.tsx`, `frontend/features/ingest/preview-sheet.tsx`.
- Related backend: none modified.

## Deliverables

- [x] 8 screens with substantively changed information hierarchy, interaction model, or spatial composition — see [`01_SPEC.md`](01_SPEC.md) for the per-screen record.
- [x] 8 screens verified against the same bar and left unchanged, with the rationale recorded rather than left implicit.
- [x] One cross-cutting bug fixed in both places it occurred.
- [x] Full verification pass recorded in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md): type-check, full-repo lint, production build, backend suite, Docker builds, diff-scope audit.
- [x] `.gitignore` gained `backend/.dev-data-ux10/` — infrastructure cleanup, not a product change; see [`CURRENT_STATE.md`](CURRENT_STATE.md) Known Issues.

## Dependencies

Depends on Phase 09 (Frontend Reimagine) — reuses its design tokens, shared components (`DataList`, `FilterRail`, `Tabs`, `SectionHeading`, etc.), and app shell without modification. Phase 09 is Released & Frozen; this phase did not reopen it.

## Milestones

None formally defined — implementation proceeded screen-by-screen in the dependency-safe order the plan specified (Knowledge → Secrets → Notes → Projects → Workbench → Model Playground → Documents → the remaining zero-coupling screens), tracked as an informal task list for the session rather than as checkpointed milestones. See [`CURRENT_STATE.md`](CURRENT_STATE.md) Session Notes for the actual sequence.
