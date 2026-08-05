# Developer Toolkit — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved in principle by the project owner 2026-08-05.
> **Last Updated:** 2026-08-05

---

## 1. Backend tests

No new backend logic is introduced (see [`03_BACKEND.md`](03_BACKEND.md)), so no new unit or integration test is required for new behavior. What's required is **regression confirmation**:

- `backend/tests/test_generators.py` and `backend/tests/test_crypto.py` (existing, covering every endpoint in [`06_API.md`](06_API.md) §1) must pass unmodified — their existence confirms this phase's "no backend behavior change" claim rather than merely asserting it.
- `backend/tests/test_workbench.py` (existing) must pass; inspected during this specification pass and confirmed to **not** hard-code the `"generators"`/`"crypto"`/`"utilities"` key names, so the `WORKBENCH_TOOL_KEYS` merge ([`01_SPEC.md`](01_SPEC.md) §3 requirement 4) is not expected to require a test change — this should be re-confirmed once the merge actually lands, not assumed to remain true.
- No test exists today for a "Utilities" backend module because none exists (see [`01_SPEC.md`](01_SPEC.md) §6) — nothing to regress-test there.

## 2. Frontend tests

`frontend/package.json` has no test script and no test framework dependency today — confirmed during this specification pass, not assumed. This is an existing, repository-wide gap (also noted, unresolved, in Universal Converter's own `07_TESTING.md` §2 for the same reason), **not something this phase's scope requires fixing**. Choosing and introducing a frontend test framework is a cross-cutting decision affecting every feature, not a Developer Toolkit-specific one — out of scope here per [`01_SPEC.md`](01_SPEC.md) §5 ("unrelated frontend redesign") and [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) (don't expand scope to fix an unrelated gap while passing through).

In the absence of automated frontend tests, this phase relies on:
- `tsc --noEmit` (typecheck) and `npm run lint` — both must be clean.
- `next build` (production build) — must succeed, with `/developer-toolkit` present in the route manifest and `/generators`/`/crypto`/`/utilities` present as redirects, not pages.
- Manual verification (§3).

## 3. Manual verification

Enumerated because nothing above automatically covers real rendering/interaction:

- [ ] Load `/developer-toolkit` directly; confirm all three tabs render and each of the 7+8+4 tools listed in [`01_SPEC.md`](01_SPEC.md) §3 requirement 1 functions identically to its pre-change behavior (generate a password, compute a hash, decode a JWT, render a QR code, convert a timezone, etc.).
- [ ] Visit `/generators`, `/crypto`, `/utilities` directly; confirm each redirects to `/developer-toolkit?tab=<name>` with the correct tab pre-selected (not defaulting to Generators).
- [ ] Confirm the sidebar shows exactly one "Developer Toolkit" entry, and the command palette (⌘K) surfaces exactly one matching result reachable by its shortcut.
- [ ] Confirm the Workbench "Generate password" quick action still works end-to-end.
- [ ] Pin "Developer Toolkit" from the Workbench pinned-tools panel; confirm it renders as a tile (replacing where the three old tool keys, if ever pinned, would have appeared — none are in `DEFAULT_PINNED_TOOLS` today, so no default-layout migration to verify).
- [ ] Dark theme + mobile viewport (per [`02_UI.md`](02_UI.md) §4–§5): confirm no horizontal overflow and that all three tools' tabs remain usable.
- [ ] Zero console errors throughout the above.

## 4. Regression risk

Existing features this phase's changes could regress, per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) and the precedent set by Universal Converter's and Knowledge Hub's own regression sections:

- **Workbench pinned tools / quick actions** — the `WORKBENCH_TOOL_KEYS` catalog and `tool-metadata.ts` map are both edited; verify no other pinned tile (Secrets, Notes, Documents, Converters, Search, etc.) is affected by the merge.
- **Command palette / global search** — confirm no unrelated palette result (Secrets, Notes, Documents, Knowledge, Projects, Converters, Prompt Studio, Model Playground, Settings) changes behavior; only the three Developer Toolkit-related entries collapse to one.
- **`frontend/features/generators/`, `frontend/features/crypto/`, `frontend/features/utilities/`** — every existing tool must be verified individually (§3) since these are exactly the components moved, and a copy/relocation error (wrong import, dropped prop) is the realistic failure mode for a consolidation phase, not a logic bug.
- **`docker compose build`** — both images must still build clean with the new/removed routes.

## 5. TODO

- [ ] None outstanding for this document specifically — pending the same overall project-owner review noted in [`01_SPEC.md`](01_SPEC.md) §8.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
