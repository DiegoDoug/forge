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

- [x] FR1 — **Verified.** `/developer-toolkit` renders three tabs (Generators, Crypto, Utilities). Within each tab, the existing feature components from that area's current standalone page are present, unmodified, with their existing configuration (props), ordering, and grid/tab structure preserved — verifiable by diffing the new page's composition against the retired page's, component for component. Visual and layout regression is covered separately by the UX criteria in §2, not by this criterion.
- [x] FR1a — **Verified live.** Every one of the 7 Generators components, the Crypto page's 4 nested tabs (with all sub-tools inside each), and the 4 Utilities components render and function identically to their current standalone-page behavior — verified by exercising each tool (generate a password, hash a string, decode a JWT, generate a QR code, etc.) and confirming output matches pre-change behavior.
- [x] FR2 — **Verified.** `GET /generators`, `GET /crypto`, and `GET /utilities` each redirect (non-permanent) to `/developer-toolkit?tab=<name>`, and the destination page loads with the corresponding tab pre-selected, not defaulting to Generators.
- [x] FR3 — **Verified.** `frontend/lib/nav-registry.ts` contains exactly one entry for Developer Toolkit; the three old entries (Generators, Crypto, Utilities) are gone. The sidebar shows one row; the command palette (⌘K) shows one matching result, reachable by its shortcut key.
- [x] FR4 — **Verified end-to-end.** `WORKBENCH_TOOL_KEYS` in `backend/app/services/workbench.py` contains a single `"developer_toolkit"` key (`available: true`); the three retired keys (`"generators"`, `"crypto"`, `"utilities"`) are absent. `GET /api/workbench/layout` (or equivalent) no longer offers the three retired keys as pinnable tools and does offer `developer_toolkit`. `frontend/features/workbench/tool-metadata.ts`'s `NAV_KEY_BY_HREF` reflects the same merge.
- [x] FR5 — **Verified.** The Workbench "Generate password" quick action navigates to the unified page's Generators tab (either directly, or via the FR2 redirect) and lands the user on a working password generator.
- [x] FR6 — **Verified.** The **implementation** of the three feature areas is unmodified: a full-repo diff shows zero changes to the contents of `backend/app/api/routes/generators.py`, `backend/app/api/routes/crypto.py`, `backend/app/services/generators/`, `backend/app/services/crypto/`, and every file under `frontend/features/generators/`, `frontend/features/crypto/`, `frontend/features/utilities/`.

  **Explicitly permitted, and not a violation of this criterion:** the new unified page importing those existing components; page-level composition and import wiring; and relocation of a file whose contents are unchanged. What this criterion prohibits is *editing the components' or services' own logic, markup, or behavior* — not building a new page out of them. (Duplicating a component's source into the new page instead of importing it is prohibited by [`IMPLEMENT.md`](IMPLEMENT.md)'s "import, not copy" execution rule, which is the counterpart to this criterion.)
- [x] FR7 — **Verified.** `docker compose up` and manual `curl` calls to `/api/generators/password`, `/api/crypto/hash`, etc. succeed unchanged, same request/response shapes as before this phase (see [`06_API.md`](06_API.md)).
- [x] FR8 — **Verified.** `package.json`/`requirements`/`pyproject.toml` show no new dependency added by this phase's diff.
- [x] FR9 — **Verified.** Every Generators/Crypto API call in the unified page still requires an authenticated session (a logged-out request to `/api/generators/*` or `/api/crypto/*` still returns 401/redirects to unlock, unchanged from today).

## 2. UX acceptance criteria

Derived from [`02_UI.md`](02_UI.md) — every screen has empty/loading/error states, keyboard access confirmed. All verified 2026-08-05 against the real Docker instance at `localhost:8585`:

- [x] The three sections' existing empty/loading/error states are preserved unmodified. Confirmed by FR6's zero-diff (no component was edited) plus live observation of each section's populated and pre-run states ("Output will appear here" placeholders intact on Base64/Hash, entropy estimator's "Empty / 0 bits" initial state, etc.).
- [~] **Partially verified — one item deferred to [`QA/QA-0001-tab-keyboard-activation.md`](QA/QA-0001-tab-keyboard-activation.md).** Confirmed: focus reaches each top-level tab; correct ARIA semantics (`role="tablist"` + three `role="tab"` + matching `tabpanel`); `ArrowRight` moves focus between tabs; every control inside the active tab is reachable. **Not confirmed:** `Enter`/`Space` did not *activate* the focused tab under automation. This is **not a Phase 08 regression** — the unmodified, uncontrolled nested Crypto tab set (byte-for-byte the pre-Phase-08 markup) behaves identically, so the behavior belongs to the shared `components/ui/tabs.tsx` primitive or to the automation harness's synthetic events. A real-keyboard session is needed to tell those apart; see the QA ticket.
- [x] Usable at mobile widths — verified at 375×812: `document.documentElement.scrollWidth === window.innerWidth === 375`, zero horizontal overflow, both tab levels visible and tappable, tools stacked single-column.
- [x] Dark and light theme both render correctly — verified by screenshot in each, no unstyled or broken elements. (The instance's stored theme was temporarily switched to light for this check and restored to its prior unset state afterwards.)
- [x] The command palette shows exactly one "Developer Toolkit" result with its `U` shortcut and no Generators/Crypto/Utilities entries; activating it navigates to `/developer-toolkit`. The palette links to the page root, not a `?tab=` deep link — consistent with how every other nav-registry-derived palette entry behaves, and the parenthetical in this criterion made that optional.
- [x] **Zero console messages** — verified in a fresh tab across a full exercise of all three tabs plus a live server-side generator call. (Errors seen earlier in the session were the pre-fix BUG-0001 500s and pre-unlock 401s, both stale buffer entries.)

## 3. Quality acceptance criteria

- [x] All tests in [`07_TESTING.md`](07_TESTING.md) pass.
- [x] No architectural invariant violated (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2) — verified by grep: no file under `frontend/features/{generators,crypto,utilities}/` imports from another feature. The new page imports from all three, which is the page layer's normal composition role, not a features-importing-features violation.
- [x] `npm run lint` and `tsc --noEmit` both clean.
- [x] Full backend test suite passes with zero regressions — **292 passed** before this phase's own test was added, identical to the pre-Phase-08 baseline; **293 passed** after adding the BUG-0001 regression test. No pre-existing test required modification.
- [x] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied.
- [x] Production frontend build (`next build`) succeeds; `/developer-toolkit` present in the route manifest; `/generators`, `/crypto`, `/utilities` absent as pages and serving 307 redirects instead. `docker compose build` also clean for both images, and the built images were deployed and verified live.

## 4. Regression criteria (no backend acceptance criteria beyond §1 — see below)

Per [`01_SPEC.md`](01_SPEC.md) §1 and [`03_BACKEND.md`](03_BACKEND.md), this phase requires **no backend service or schema changes** beyond the `WORKBENCH_TOOL_KEYS` catalog edit already covered by FR4. There is therefore no separate backend acceptance section beyond §1's functional criteria — regression verification (§1 FR6/FR7/FR9) is the applicable check in place of new backend acceptance criteria.

- [x] `/search` and the global command palette's non-Developer-Toolkit results are unaffected — `/search?q=forge` returns real results across Secrets and Documents; the palette's other twelve entries (Workbench, Secrets, Notes, Documents, Knowledge, Projects, Converter, Project Init, Prompt Studio, Model Playground, Settings, Lock) are all present and unchanged.
- [x] No other Workbench panel regresses — Pinned Tools, Quick Actions, Storage & System, Recent Notes, and Recent Activity all render correctly. **Note:** this criterion initially FAILED — see [`BUGS/BUG-0001-stale-pinned-tool-key-500.md`](BUGS/BUG-0001-stale-pinned-tool-key-500.md), a BLOCKER in which the tool-key merge 500'd the entire Workbench for any user whose saved layout pinned a retired key. Fixed, regression-tested, and re-verified against the same real layout that exhibited it.
- [x] Existing Generators/Crypto/Utilities-referencing tests still pass unmodified — `test_generators.py`, `test_crypto.py`, and `test_workbench.py` all pass with **zero edits to any pre-existing test**. The only test change in this phase is one *added* regression test for BUG-0001.

## 5. Sign-off

- [ ] **Awaiting project-owner sign-off.** Every criterion above is checked with cited evidence, with two things explicitly *not* claimed as clean: the keyboard-activation item in §2 is deferred to [`QA/QA-0001`](QA/QA-0001-tab-keyboard-activation.md) (pre-existing, not a Phase 08 regression), and §4 records that the Workbench regression criterion failed before [`BUGS/BUG-0001`](BUGS/BUG-0001-stale-pinned-tool-key-500.md) was fixed rather than presenting it as having passed first time.
- [ ] TODO: who signs off on this phase being complete? (Same open item as every other Phase 08 doc — project owner to assign.)

## 6. TODO

- [x] `01_SPEC.md` §7's open questions all resolved as proposed (2026-08-05), so no criterion here needed rewording for a changed route slug or layout decision.
- [x] Project-owner corrections applied 2026-08-05: FR1 no longer requires "pixel-identical" tab content (it now requires preserved components/configuration/ordering/behavior, with visual and layout regression covered by §2's UX criteria instead); FR6 now states explicitly that page-level composition, import wiring, and content-preserving relocation are permitted, so it cannot be read as forbidding the new page from importing the existing components.

## 7. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
