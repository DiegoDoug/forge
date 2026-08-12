# UX Elevation — Acceptance / Verification Record

> **Purpose:** What was actually verified for Phase 10, and how. This is the implementation/verification source of truth for the phase — it reflects the release-readiness pass run after implementation, not a pre-agreed `VERIFICATION_CONTRACT.md` (none was written in advance for this phase — see [`README.md`](README.md)'s process note).
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Complete — release candidate. No owner sign-off recorded yet; not committed or tagged.
> **Version:** 1.0.0
> **Last Updated:** 2026-08-12
> **Depends On:** [`01_SPEC.md`](01_SPEC.md)

---

## 1. How to use this document

Each criterion is checked with the actual evidence gathered during the release-readiness pass — a command, its output, or a live-browser measurement taken this session. Nothing here is inferred or assumed from the diff alone.

## 2. Scope and diff integrity

**AC1** ✅ — All changes are frontend-only; zero backend/docker files touched. **Evidence:** `git diff --stat -- backend/ docker/` returned empty output.

**AC2** ✅ — The full diff was read hunk-by-hunk and every change traced to an intended Phase 10 screen or the cross-cutting Sheet-header fix (§4 of `01_SPEC.md`). **Evidence:** `git diff --stat` — 23 tracked files, `317 insertions(+), 114 deletions(-)`, all under `frontend/` plus one `.gitignore` line (see AC9).

**AC3** ✅ — No stray untracked files staged for commit. **Evidence:** `git status` after the `.gitignore` fix (AC9) shows only the 23 intended tracked modifications; `backend/.dev-data-ux10/` (the throwaway verification instance's seeded data) does not appear as untracked.

## 3. Static verification

**AC4** ✅ — TypeScript compiles clean across the whole frontend. **Evidence:** `npx tsc --noEmit` — zero output, zero errors.

**AC5** ✅ — ESLint clean across the **whole repository**, not just touched directories. **Evidence:** `npm run lint` (which runs bare `eslint`, repo-wide) — zero output, zero errors/warnings. One warning (`'DataListRow' is defined but never used` in `knowledge-result-list.tsx`) was found and fixed mid-session before this final clean run.

## 4. Build verification

**AC6** ✅ — Production build succeeds. **Evidence:** `npm run build` (`next build --turbopack`) — `✓ Compiled successfully`, `✓ Generating static pages (19/19)`, zero errors.

**AC7** ✅ — All 17 application routes compile and prerender/route correctly. **Evidence:** build output route table lists all 17 (`/`, `/converters`, `/developer-toolkit`, `/documents`, `/knowledge`, `/model-playground`, `/notes`, `/project-init`, `/projects`, `/projects/[id]`, `/prompt-studio`, `/search`, `/secrets`, `/settings`, `/setup`, `/unlock`, plus `/_not-found`), each with a reported bundle size and no build-time error.

**AC8** ✅ — Docker images for both frontend and backend build cleanly from the working tree. **Evidence:** `docker build -f frontend/Dockerfile frontend` and `docker build -f backend/Dockerfile backend` both completed (`DONE`, image exported); the frontend image's own build step reproduced the same 17-route table as AC7 inside the container. Both throwaway images (`forge-frontend-ux10-check`, `forge-backend-ux10-check`) removed after verification — not left in the local Docker image store.

## 5. Backend regression

**AC9** ✅ — Backend test suite is fully green; no backend code was touched by this phase. **Evidence:** `pytest` — `293 passed, 50 warnings in 25.55s`, 0 failed, 0 errors. The 50 warnings are pre-existing deprecations (`StarletteDeprecationWarning` on `HTTP_422_UNPROCESSABLE_ENTITY`, an `httpx`/`starlette.testclient` deprecation notice, and a benign `RuntimeError: Event loop is closed` in a test-teardown thread for `test_knowledge_service.py`) — present before this phase touched anything, not introduced by it, and not a failure. Corroborated by AC1 (`git diff --stat -- backend/` empty), which makes a Phase-10-caused backend regression structurally impossible.

## 6. Infrastructure cleanup

**AC10** ✅ — `.gitignore` gained `backend/.dev-data-ux10/`. **Rationale:** verification of the Workbench/Notes/Model Playground/Projects redesigns required a populated instance to inspect (seeded secrets, notes, documents, projects, prompts, and one provider credential). The existing dev instances (`backend/.dev-data`, `-verify`, `-phase09`) all had unknown master passwords, so a new throwaway instance (`backend-ux10`/`frontend-ux10`, ports 8004/3004) was created and seeded via the real API — the same pattern Phase 09 used for its own `-phase09` instance. Every prior instance is listed individually in `.gitignore`; this one was not, until this fix. Without it, a broad `git add -A` at commit time would have staged a live SQLite database containing seeded (fake) secret values.

**AC11** ✅ — `.claude/launch.json` (which gained `backend-ux10`/`frontend-ux10` entries during this phase) is **not** a tracked Phase 10 change. **Evidence:** `git check-ignore -v .claude/launch.json` — matched by `.gitignore:39` (`.claude/`), confirmed via `git status` showing no `.claude/` entries in the diff at any point.

## 7. Live UX verification, per screen

Verified using the Browser preview tools (live DOM inspection, computed styles/geometry, real interaction) against the seeded `frontend-ux10` instance — not screenshots alone, per the plan's own stated verification approach.

**AC12** ✅ — **Breakpoints.** Workbench, Notes, Model Playground, and Prompt Studio (the screens with structural composition changes) were checked at 375px, 768px, and 1440px. **Evidence:** live screenshots and `read_page`/computed-geometry checks at each width per screen — e.g. Workbench's primary/rail split confirmed to stack correctly below `lg` with primary-column content (Pinned Tools, Recent Notes, Recent Projects) ordered before rail content on mobile; Prompt Studio's Body-first ordering confirmed present in the mobile DOM via `get_page_text`.

**AC13** ✅ — **Both themes.** **Evidence:** switched the seeded instance to light mode via Settings (confirmed via `document.documentElement.className` containing `light`, since a UI-click on the theme toggle silently failed to persist on the first attempt — resolved by dispatching the click via `querySelector(...).click()` directly) and re-screenshotted Workbench and Notes; both render correctly. Reverted to dark afterward.

**AC14** ✅ — **Navigation/deep-link contracts.** Every nav edge touched by a redesigned screen was replayed, not just assumed unchanged:
- Knowledge's note-result link resolves to `/notes?open={id}` and lands with the scroll-and-highlight effect firing (confirmed via computed `boxShadow`/ring class on the correct note, keyed by real distinct canvas positions after correcting a seed-data artifact that had stacked all three notes at `(0,0)`).
- Project Detail's newly-added scoped-list deep links (`/secrets?project_id=…&open=…`, equivalently for notes/documents) confirmed to open the correct detail sheet — walked through a real secret via this path and confirmed the `SecretDetailSheet` opened with the right content.
- Workbench's pinned-tool, quick-action, and panel-deep-link hrefs re-confirmed present and unchanged via `read_page` after the layout restructure (7 pinned-tool targets, 3 quick actions, 2 panel deep links).

**AC15** ✅ — **Workbench panel-registry contract.** **Evidence:** `getRegisteredPanels()`/`register-all.ts` import ordering untouched (diff-verified — only additive `column` field added to `WorkbenchPanelMetadata` and per-panel registration calls); customize-mode visibility toggle exercised live (toggled "Recent Notes" off via a direct `.click()` on the underlying Base UI Switch element — a synthetic `computer`-tool click did not register the first several attempts, confirmed via `PUT /api/workbench/layout` firing only on the direct dispatch, a pre-existing Base UI Switch/tooling interaction quirk unrelated to this phase's changes) and confirmed the panel correctly dims and is labeled "Hidden" without disappearing from the customize-mode layout.

**AC16** ✅ — **`useKnowledgeList` contract preserved.** **Evidence:** diff of `features/knowledge/api.ts` is empty — the 4-parameter filter shape (`q`, `type`, `project_id`, `tag_id`, no pagination) was not touched; Documents' and Notes' existing reach-through consumption of this hook (`useKnowledgeList({type:"document"})` / `{type:"note"}`) was not modified and continues to compile and run (AC4, AC6).

## 8. What was not verified

- No frontend automated test suite exists in this repository (confirmed via `package.json` — no `test` script), consistent with Phase 09's own recorded Known Issue #2. Regression safety for this phase rests on type-check + full-repo lint + production build + live manual verification, the same compensating approach Phase 09 used.
- Screen-reader / assistive-technology verification was not performed for the screens changed in this phase. Phase 09's accessibility baseline (T27) was not re-audited; no new icon-only controls or unlabeled interactive elements were introduced by this phase's changes, but that claim was not independently re-verified with a screen reader.
- The Sheet-header fix (§4 of `01_SPEC.md`) was live-verified via computed geometry on the Secrets detail sheet only; the second affected consumer (`features/ingest/preview-sheet.tsx`) received the structurally identical fix but was not independently re-verified live, since reproducing a completed ingest job was out of proportion to the fix's risk (a single Tailwind class addition, same pattern confirmed working elsewhere).
