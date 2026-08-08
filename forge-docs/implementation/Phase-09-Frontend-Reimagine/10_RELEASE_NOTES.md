# Frontend Reimagine — Release Notes

> **Purpose:** What shipped in this phase, written for someone who uses Forge rather than builds it.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** ✅ **Implementation complete. Ready for Release Candidate**, pending owner sign-off. T0–T30 done and verified 2026-08-06/07. See [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) for the full criterion-by-criterion record and [`../../../.design/frontend-reimagine/DESIGN_REVIEW.md`](../../../.design/frontend-reimagine/DESIGN_REVIEW.md) for T30's design-review findings.
> **Target version:** `v0.9.0-frontend-reimagine` *(proposed — not tagged; tagging happens at Release, not RC)*
> **Last Updated:** 2026-08-06

---

## 1. Status

All 30 tasks (T0–T28) are complete. Every claim in this document reflects what actually shipped, not a target — corrected against `09_IMPLEMENTATION_TASKS.md`'s as-built notes and `08_ACCEPTANCE.md`'s evidence, not carried forward from the pre-implementation placeholder this document used to be. One claim from the placeholder version was **removed** as unverified (see §3, Changed) rather than left in place unchecked.

Per the repo convention ([`../RELEASE_NOTES_TEMPLATE.md`](../RELEASE_NOTES_TEMPLATE.md)), full **Released** status still requires T30 (`/design-review`) and owner sign-off.

## 2. Headline

> Forge looks and works like one product.

Same capabilities, same routes, same data — a coherent visual language, a navigable information architecture, genuinely responsive layouts, and an accessibility baseline the project has never had.

## 3. User-visible changes

### Fixed

- **Forge renders in its intended typeface.** The application had been rendering entirely in the browser's default serif — Times New Roman — because of a self-referential CSS variable. The Geist typeface was downloaded on every page load and never applied. This affected every screen since the project began.
- **The Settings storage readout works.** The About card's storage line had never rendered, because the endpoint it reads was not reachable from the browser.
- **Deleting a document, a note, or a generated scaffold now asks first.** Also closed, found during Milestone 4's audit rather than pre-identified: Secrets' folder and tag delete buttons, and Settings' "Import backup" — the single most destructive action in the app, which replaces every secret, folder, tag, and note, and previously had no confirmation gate at all.
- **Secrets and Documents are usable on a phone.** Both pinned a fixed-width rail with no responsive handling, leaving 151px and 87px of content respectively at a 375px viewport; Secrets additionally overflowed horizontally at 768px, a second distinct bug sharing the same root cause.
- **The command palette's Knowledge shortcut now actually works.** Found during final regression validation: Knowledge's advertised shortcut was "K" — the same key that opens and closes the palette — so it was unreachable specifically while the palette was already open, the one shortcut letter with this collision.
- **Secrets and Documents no longer lose ~80–110px of content width on phones and tablets.** Found during the final design review: the mobile filter-drawer trigger was reserving its own column of space next to the content instead of stacking above it, on the two surfaces that use it. Fixed at the layout level; nothing about the drawer's behavior otherwise changed.
- **Notes deep-linked from search or the Knowledge Hub now land on the actual note**, scrolled into view with a momentary highlight, instead of a bare, unindicated board.

### Changed

- **The sidebar is grouped** — Workspace, Library, Build, Tools — with Settings pinned separately as app configuration. Same twelve destinations, ranked.
- **Search has one obvious entry point.** ⌘K finds anything — secrets, notes, documents, and every destination — with a path to the full result set. Knowledge Hub is now clearly a place to browse and organise notes and documents, rather than a third thing that also searches.
- **The keyboard shortcuts Forge advertised now work.** Eight destination shortcuts were displayed in the command palette but bound to nothing.
- **Every screen has a real empty, loading, and error state**, and "no results for your filters" is now distinguishable from "nothing here yet".
- **Light and dark themes both meet WCAG AA contrast** — the first time Forge has had a stated contrast standard. One real violation (Secrets' tag badges) was found and fixed in the process.
- **Icon-only controls have real accessible names.** 16 controls across Secrets, Notes, and the shared copy/generator components had none.
- **The sidebar's navigation groups are now legible to screen readers**, not just visually — previously hidden behind `role="presentation"`.
- **Reduced-motion preferences are respected.** Every transition/animation collapses to near-zero duration when the OS-level preference is set.

### Unchanged — deliberately

- Every route and URL, including all existing bookmarks and redirects.
- Every API contract, every capability, and all your data.
- The scope of every search surface: `/search` still finds secrets as well as notes and documents.

### Correction (RC verification pass, 2026-08-07)

- **"Reduced-motion preferences are respected" is back on this list — it was wrongly removed at T29.** The T29 documentation pass incorrectly treated this as an unverified claim and struck it. RC verification found and live-confirmed a substantive `prefers-reduced-motion` block in `globals.css` that zeroes every motion token and forces near-zero transition/animation durations — measured directly (`transitionDuration: 1e-05s`, `--duration-normal: 0s`) with the preference active, not just read from source. See [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) AC43.

## 4. Technical summary

- Three-layer design token system in `globals.css`, preserving the existing shadcn semantic contract by name ([ADR-0017](../../decisions/0017-layered-design-token-architecture.md)).
- Grouped navigation and a resolved search model ([ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md)).
- One `AppShell` owning layout and scroll containment; three hardcoded viewport calculations removed.
- Duplicated patterns consolidated: list containers → `DataList`, search inputs → `SearchField`, error blocks → `ErrorState`, every delete → `ConfirmDialog`, plus new `FilterRail`, `Toolbar`, `SectionHeading`, `StatusBadge`, `Field`, `KeyValueRow`.
- One primitive (`table.tsx`, zero consumers) and one dependency (`framer-motion`, zero import sites) removed; zero new runtime dependencies added.
- **Zero backend changes across all 30 tasks.** One `next.config.ts` rewrite made an already-shipped endpoint reachable in development; the equivalent production gap (`docker/nginx.conf` doesn't proxy `/system/status`) was found, raised, and tracked in [`../../../docs/Roadmap.md`](../../../docs/Roadmap.md) rather than patched, since `docker/**` was inspect-only under this phase's contract.
- Backend test suite: 100% pass, unchanged, verified at final regression validation (T28).

## 5. Known limitations at release

- Forge still has no frontend test framework. Regression safety in this phase rested on a captured baseline, typecheck, lint, build, and disciplined manual verification ([`07_TESTING.md`](07_TESTING.md) §8) — including a full 48-navigation-edge sweep at T28, which is where the Knowledge-shortcut collision above was actually found.
- No automated accessibility tool (`axe` or equivalent) exists in this project's toolchain. T27 substituted live-measured contrast checking and a manual `aria-label`/landmark sweep, which found and fixed 6 real defects — but this is not equivalent to an automated scan's coverage. A real screen-reader pass and a proper `axe` pass are both tracked as QA tickets, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §3.
- **Dialog focus does not return to its trigger on close.** Verified live at RC: opening a dialog correctly traps focus inside it, but closing it (via Escape or its own Close button) leaves focus stranded rather than restoring it to the button that opened it. Pre-existing Base UI integration behavior, not introduced by this phase, but a real, currently-open gap. See [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) AC41.
- **Form-error `aria-describedby` association exists but isn't uniform.** The shared `Field` component wires it correctly, but only one form in the entire app uses it. See [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) AC45.
- List-endpoint pagination remains a backend gap; surfaces continue to show an honest truncation notice.
- `/design-review` (T30) ran and found two non-blocking Should Fix items, left for a follow-up decision rather than fixed in this phase: a pre-existing (not Phase 09-introduced) decorative gradient on the auth screens with no functional purpose, and a document-title input that visibly truncates at 768px because its action toolbar doesn't yet collapse to an overflow menu. See [`../../../.design/frontend-reimagine/DESIGN_REVIEW.md`](../../../.design/frontend-reimagine/DESIGN_REVIEW.md).

## 6. Upgrade notes

None anticipated — no schema change, no migration, no configuration change, no bookmark breakage. Verified: `git diff --stat backend/ docker/` stayed empty across all 30 tasks.

## 7. Cross-references

- [README.md](README.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [CURRENT_STATE.md](CURRENT_STATE.md) · [00_AUDIT.md](00_AUDIT.md)
- [../RELEASE_NOTES_TEMPLATE.md](../RELEASE_NOTES_TEMPLATE.md)
