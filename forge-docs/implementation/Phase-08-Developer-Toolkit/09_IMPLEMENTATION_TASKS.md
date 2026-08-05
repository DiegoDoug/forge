# Developer Toolkit — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** All ten tasks complete (2026-08-05). Implementation authorized 2026-08-05; executed and verified the same day. One BLOCKER was found during T8 and fixed — see [`../../history/Phase-08/BUGS/BUG-0001-stale-pinned-tool-key-500.md`](../../history/Phase-08/BUGS/BUG-0001-stale-pinned-tool-key-500.md).
> **Last Updated:** 2026-08-05

---

## 1. Task list

Given this phase's small, precedent-following shape (no backend/database work), one milestone rather than Universal Converter's seven — see §2. All ten completed 2026-08-05.

One task list item is *not* in the original ten, and is recorded here rather than folded in silently: fixing [`BUGS/BUG-0001`](../../history/Phase-08/BUGS/BUG-0001-stale-pinned-tool-key-500.md), a BLOCKER that T5's catalog merge exposed and that T8 caught. It was in scope as a direct consequence of approved work (see that bug's "Scope note"), and carried its own regression test.

- [x] T1 — Create `app/(app)/developer-toolkit/page.tsx`: top-level `Tabs` (Generators / Crypto / Utilities), each `TabsContent` importing the existing, unmodified components per [`01_SPEC.md`](01_SPEC.md) §3 requirement 1. Read `?tab=` search param to preselect the active tab.
- [x] **T2 + T3 — atomic; must land as a single implementation change, never separately.**
  - T2 — Delete `app/(app)/generators/page.tsx`, `app/(app)/crypto/page.tsx`, `app/(app)/utilities/page.tsx` (their content now lives in T1's page; the routes themselves become redirects, not pages).
  - T3 — Add three entries to `next.config.ts`'s `redirects()`: `/generators`, `/crypto`, `/utilities` → `/developer-toolkit?tab=<name>` (`permanent: false`), per [`01_SPEC.md`](01_SPEC.md) §3 requirement 2.
  - **Atomicity requirement:** the page deletions and the redirect entries must be committed together. At no point in the implementation sequence — including intermediate commits, partial checkouts, or a reviewer checking out any single commit on this branch — may `/generators`, `/crypto`, or `/utilities` resolve to a 404. Deleting the pages first and adding redirects afterwards is explicitly out of contract, even if the end state is correct.
- [x] T4 — Replace `frontend/lib/nav-registry.ts`'s three entries (Generators/Crypto/Utilities) with one entry: title "Developer Toolkit", href `/developer-toolkit`, icon `Wrench`, shortcut `U` (confirmed 2026-08-05 — see [`02_UI.md`](02_UI.md) §2).
- [x] T5 — Update `backend/app/services/workbench.py`'s `WORKBENCH_TOOL_KEYS`: remove `"generators"`, `"crypto"`, `"utilities"`; add `"developer_toolkit"` (`available: true`). Add a code comment documenting this merge, mirroring the existing Phase 04 precedent comment already in that file.
- [x] T6 — Update `frontend/features/workbench/tool-metadata.ts`'s `NAV_KEY_BY_HREF`: collapse the three existing entries into one (`/developer-toolkit` → `developer_toolkit`).
- [x] T7 — Update `frontend/features/workbench/components/quick-actions-panel.tsx`'s "Generate password" quick action href to `/developer-toolkit?tab=generators`.
- [x] T8 — Manual verification pass per [`07_TESTING.md`](07_TESTING.md) §3 (every tool exercised, redirects confirmed, palette/sidebar confirmed, dark/mobile checked).
- [x] T9 — Regression pass per [`07_TESTING.md`](07_TESTING.md) §4: full backend suite (`test_generators.py`, `test_crypto.py`, `test_workbench.py`, full suite for zero-regression count), `tsc --noEmit`, `npm run lint`, `next build`, `docker compose build`.
- [x] T10 — Documentation sweep: update `docs/Architecture.md`, `docs/API.md` (if route table needs a Developer Toolkit row), `docs/FolderStructure.md`, root `README.md`, `forge-docs/02_ROADMAP.md` (Phase 08 row), and this phase's own `CURRENT_STATE.md`/`README.md` to reflect the shipped state — mirroring Universal Converter's Milestone 6 precedent.

## 2. Task ordering notes

- **T2 and T3 are a single atomic change, not two sequential tasks** (see their entry in §1). Deleting the old pages without the redirects already in place would 404 existing bookmarks at that commit — matching [`01_SPEC.md`](01_SPEC.md) §3 requirement 2's explicit "redirect, not 404" requirement, which this ordering note enforces at every intermediate point in the sequence, not just at the end state.
- T4–T7 (nav/workbench catalog updates) can proceed in parallel with or immediately after T1–T3; none blocks the others.
- T8–T9 (verification) follow all implementation tasks.
- T10 (docs) follows verification, once the shipped shape is final — not drafted speculatively ahead of the code, consistent with [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.3 (no fake completeness).
- All ten tasks are proposed to fit in a **single milestone** (unlike Universal Converter's seven), since there is no backend abstraction to stage in separately, no migration to sequence, and no multi-step provider integration — the entire phase is one coherent page/nav/routing change plus its verification and docs.

## 3. TODO

- [x] Project-owner confirmation of this breakdown — **approved in principle 2026-08-05**, with the T2/T3 atomicity correction applied.
- [x] Explicit implementation authorization before T1 starts — **granted 2026-08-05**, recorded in [`IMPLEMENT.md`](IMPLEMENT.md)'s Status line as a gate distinct from specification approval.
- [x] T2+T3 atomicity held in practice, not just on paper: both landed in commit `62cbd54` together. Verified by `curl` against both the dev server and the production nginx path — all three legacy routes return 307 to their `?tab=` destination, never 404.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
