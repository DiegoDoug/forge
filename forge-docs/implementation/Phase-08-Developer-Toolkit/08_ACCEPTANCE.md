# Developer Toolkit — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved in principle by the project owner 2026-08-05, with three requested corrections applied the same day (FR1 wording, FR6 wording, and T2/T3 atomicity in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)). Awaiting explicit implementation authorization — see [`IMPLEMENT.md`](IMPLEMENT.md).
> **Version:** 0.2.0
> **Last Updated:** 2026-08-05

---

## 1. Functional acceptance criteria

Traceable to [`01_SPEC.md`](01_SPEC.md) §3:

- [ ] FR1 — `/developer-toolkit` renders three tabs (Generators, Crypto, Utilities). Within each tab, the existing feature components from that area's current standalone page are present, unmodified, with their existing configuration (props), ordering, and grid/tab structure preserved — verifiable by diffing the new page's composition against the retired page's, component for component. Visual and layout regression is covered separately by the UX criteria in §2, not by this criterion.
- [ ] FR1a — Every one of the 7 Generators components, the Crypto page's 4 nested tabs (with all sub-tools inside each), and the 4 Utilities components render and function identically to their current standalone-page behavior — verified by exercising each tool (generate a password, hash a string, decode a JWT, generate a QR code, etc.) and confirming output matches pre-change behavior.
- [ ] FR2 — `GET /generators`, `GET /crypto`, and `GET /utilities` each redirect (non-permanent) to `/developer-toolkit?tab=<name>`, and the destination page loads with the corresponding tab pre-selected, not defaulting to Generators.
- [ ] FR3 — `frontend/lib/nav-registry.ts` contains exactly one entry for Developer Toolkit; the three old entries (Generators, Crypto, Utilities) are gone. The sidebar shows one row; the command palette (⌘K) shows one matching result, reachable by its shortcut key.
- [ ] FR4 — `WORKBENCH_TOOL_KEYS` in `backend/app/services/workbench.py` contains a single `"developer_toolkit"` key (`available: true`); the three retired keys (`"generators"`, `"crypto"`, `"utilities"`) are absent. `GET /api/workbench/layout` (or equivalent) no longer offers the three retired keys as pinnable tools and does offer `developer_toolkit`. `frontend/features/workbench/tool-metadata.ts`'s `NAV_KEY_BY_HREF` reflects the same merge.
- [ ] FR5 — The Workbench "Generate password" quick action navigates to the unified page's Generators tab (either directly, or via the FR2 redirect) and lands the user on a working password generator.
- [ ] FR6 — The **implementation** of the three feature areas is unmodified: a full-repo diff shows zero changes to the contents of `backend/app/api/routes/generators.py`, `backend/app/api/routes/crypto.py`, `backend/app/services/generators/`, `backend/app/services/crypto/`, and every file under `frontend/features/generators/`, `frontend/features/crypto/`, `frontend/features/utilities/`.

  **Explicitly permitted, and not a violation of this criterion:** the new unified page importing those existing components; page-level composition and import wiring; and relocation of a file whose contents are unchanged. What this criterion prohibits is *editing the components' or services' own logic, markup, or behavior* — not building a new page out of them. (Duplicating a component's source into the new page instead of importing it is prohibited by [`IMPLEMENT.md`](IMPLEMENT.md)'s "import, not copy" execution rule, which is the counterpart to this criterion.)
- [ ] FR7 — `docker compose up` and manual `curl` calls to `/api/generators/password`, `/api/crypto/hash`, etc. succeed unchanged, same request/response shapes as before this phase (see [`06_API.md`](06_API.md)).
- [ ] FR8 — `package.json`/`requirements`/`pyproject.toml` show no new dependency added by this phase's diff.
- [ ] FR9 — Every Generators/Crypto API call in the unified page still requires an authenticated session (a logged-out request to `/api/generators/*` or `/api/crypto/*` still returns 401/redirects to unlock, unchanged from today).

## 2. UX acceptance criteria

Derived from [`02_UI.md`](02_UI.md) — every screen has empty/loading/error states, keyboard access confirmed:

- [ ] The three sections' existing empty/loading/error states (each already defined per-component today) are preserved unmodified — no regression, no new state design required (per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md), nothing new is designed where nothing new is needed).
- [ ] The unified page and its tabs are keyboard-navigable (Tab/Shift+Tab reaches each top-level tab and every control inside the active tab; Arrow keys switch tabs, matching the existing `Tabs` primitive's built-in behavior already used on the current Crypto page).
- [ ] The unified page is usable at mobile widths — no horizontal overflow, tabs remain tappable/scrollable at narrow viewports (verified per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §3).
- [ ] Dark and light theme both render correctly (no unstyled/broken elements in either).
- [ ] The command palette's single Developer Toolkit result, when activated, navigates correctly and (if a `?tab=` deep link is supported from the palette) lands on the right tab.

## 3. Quality acceptance criteria

- [ ] All tests in [`07_TESTING.md`](07_TESTING.md) pass.
- [ ] No architectural invariant violated (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2) — confirmed no cross-feature imports were introduced merging three `features/` directories' components onto one page (each keeps importing only from its own `features/<name>/`, the new page component imports from all three, which is the page layer's normal role, not a features-importing-features violation).
- [ ] `npm run lint` and `tsc --noEmit` both clean.
- [ ] Full backend test suite passes with zero regressions (same pass count as the pre-Phase-08 baseline, since no backend logic changed).
- [ ] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied.
- [ ] Production frontend build (`next build`) succeeds; `/developer-toolkit` route is present in the build output; `/generators`, `/crypto`, `/utilities` are present as redirects, not pages.

## 4. Regression criteria (no backend acceptance criteria beyond §1 — see below)

Per [`01_SPEC.md`](01_SPEC.md) §1 and [`03_BACKEND.md`](03_BACKEND.md), this phase requires **no backend service or schema changes** beyond the `WORKBENCH_TOOL_KEYS` catalog edit already covered by FR4. There is therefore no separate backend acceptance section beyond §1's functional criteria — regression verification (§1 FR6/FR7/FR9) is the applicable check in place of new backend acceptance criteria.

- [ ] `/search` and the global command palette's non-Developer-Toolkit results are unaffected (same precedent check Universal Converter and Knowledge Hub both ran).
- [ ] No other Workbench panel (recent activity, pinned tools for other tools, system status) regresses.
- [ ] Existing Generators/Crypto/Utilities-referencing tests (if any exist today) still pass unmodified, or are updated only for their new route/location, never for new expected behavior.

## 5. Sign-off

- [ ] TODO: who signs off on this phase being complete? (Same open item as every other Phase 08 doc — project owner to assign.)

## 6. TODO

- [x] `01_SPEC.md` §7's open questions all resolved as proposed (2026-08-05), so no criterion here needed rewording for a changed route slug or layout decision.
- [x] Project-owner corrections applied 2026-08-05: FR1 no longer requires "pixel-identical" tab content (it now requires preserved components/configuration/ordering/behavior, with visual and layout regression covered by §2's UX criteria instead); FR6 now states explicitly that page-level composition, import wiring, and content-preserving relocation are permitted, so it cannot be read as forbidding the new page from importing the existing components.

## 7. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
