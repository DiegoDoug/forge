# UX Elevation — Release Notes

> **Purpose:** The release-facing summary of Phase 10 — what shipped, what to check before upgrading. Not a duplicate of `CURRENT_STATE.md` (the working log) — this is what a user or another engineer reads to understand what changed.
> **Scope:** This phase only.
> **Status:** Draft — written at RC, not yet finalized (no owner sign-off, no tag).
> **Version:** Unreleased — no tag assigned yet, unlike Phases 01–09 which each shipped as `vN.N.0-name`. See `CURRENT_STATE.md` Remaining.
> **Last Updated:** 2026-08-12
> **Depends On:** [`CURRENT_STATE.md`](CURRENT_STATE.md), [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md)

---

## New Features

None — this phase changed presentation and interaction composition only, per its own scope constraint. No new product capability was added.

## Breaking Changes

None. Every navigation edge, API contract, and query hook shape used by a redesigned screen was preserved — see `08_ACCEPTANCE.md` AC14–AC16.

## Migrations

None. No database or backend change of any kind.

## Bug Fixes

- **Sheet header icon collision** — `SheetContent`'s built-in close button (top-right, absolute-positioned) rendered on top of custom header action icons on two screens: the Secrets detail sheet (pencil/trash icons, reported by the owner via an annotated screenshot) and the Ingest preview sheet (copy/save-to-notes actions, found during the follow-up audit of all `Sheet`/`Dialog` consumers). Both fixed by reserving space in the affected header row; the shared `Sheet` primitive itself was not modified.
- **Documents mobile empty-state copy** — referenced "the history on the left," which doesn't exist once the document list moves behind a drawer trigger below the `lg` breakpoint. Corrected to breakpoint-neutral wording.
- **Knowledge Hub note deep-link** — already fixed in Phase 09 (T11); reconfirmed still correct during this phase's Knowledge redesign, not re-broken.
- **Project Detail scoped-list rows were inert** — clicking a secret/note/document under a project's rollup lists did nothing; only the "View all" link worked. Now each row deep-links to the actual item via the existing `?open={id}` contract.

## Known Issues

- No formal owner sign-off has been recorded for this phase. See `CURRENT_STATE.md` Known Issues #4.
- No frontend automated test suite exists in this repository (pre-existing, Phase 09 Known Issue #2) — this phase's regression safety rests on type-check, full-repo lint, production build, and live manual verification, not automated tests.
- Screen-reader verification was not performed for the screens this phase changed. No new icon-only or unlabeled interactive elements were introduced, but that was not independently confirmed with assistive technology.

## Upgrade Notes

None beyond a normal frontend deploy. No environment variables, no data migrations, no new dependencies (`Tabs`, used in the Prompt Studio redesign, was already an existing shared primitive from Phase 09 — no new package added).

## Deferred Work

- Search's weak discoverability (no sidebar/palette entry) was identified as a real UX gap during this phase's review but deliberately **not** re-litigated here — it's already tracked as a navigation decision in [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md), and this phase's scope was screen-level composition, not navigation architecture.
- No formal `VERIFICATION_CONTRACT.md` was written in advance for this phase (see `README.md` process note); if a future phase wants Phase 10 brought fully into this repository's FDK convention, writing one retroactively — and seeking the roadmap-ratification/authorization gates Phases 01–09 went through — is that phase's work, not a correction owed here.

## Cross-references

- [`CURRENT_STATE.md`](CURRENT_STATE.md)
- [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md)
- [`01_SPEC.md`](01_SPEC.md)
- [`../Phase-09-Frontend-Reimagine/README.md`](../Phase-09-Frontend-Reimagine/README.md)
