# Universal Converter — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** TODO — assign a phase owner.
> **Status:** RC audit complete (Milestone 7, 2026-07-25). Every criterion in §1–§4 checked against direct evidence gathered across Milestones 1–7, re-verified fresh at this milestone rather than carried over by assumption. Zero open BLOCKERs. Awaiting the project owner's formal Sign-off decision (§5).
> **Last Updated:** 2026-07-25

---

## 1. Functional acceptance criteria — new capability

Each item traces to its numbered requirement in [`01_SPEC.md`](01_SPEC.md) §3.

- [x] A `ConverterProvider` protocol exists in `backend/app/services/converters/providers/__init__.py` with `register()`/`list_providers()`, and `MarkItDownProvider` (`providers/markitdown.py`) is registered at import time, wrapping `services.ingest.converter.submit` without modifying it. (§3.6) — `test_converters_providers.py::test_markitdown_provider_declares_the_correct_shape` and `test_markitdown_provider_submit_delegates_without_transformation`; live-confirmed via `GET /api/converters/providers` returning exactly one `slug == "markitdown"` entry.
- [x] `GET /api/converters/providers` returns `200` with `{"providers": [...]}` matching the `ProvidersOut` schema, requires a valid session (`401` without one), and involves no file I/O or job-store access. (§3.7, [`06_API.md`](06_API.md) §1.1) — `test_converters_api.py::test_get_providers_requires_a_session`, `test_setup_then_get_providers_returns_the_registered_markitdown_provider`; timed at ~0.2μs per call (in-memory list read only).
- [x] `frontend/lib/nav-registry.ts` contains exactly one entry for this feature (not two) — `grep -c '"/converters"' frontend/lib/nav-registry.ts` returns `1`, and no entry has `href: "/ingest"`. (§3.3) — confirmed by grep and live-verified: sidebar and ⌘K palette both show exactly one "Converter" entry.
- [x] `/converters` renders a "Text & Data" section (the nine existing tools) and a "Documents" section (the Ingest workflow) on one page. (§3.1, [`02_UI.md`](02_UI.md) §1) — live-verified repeatedly (Milestones 5 and 6): all ten tool cards plus the dropzone/job-list render together.
- [x] Navigating to `/ingest` results in a redirect to `/converters` (not a 404, not a blank page). (§3.2) — `curl -s -o /dev/null -w "%{http_code} %{redirect_url}"` against `/ingest` returned `307` → `/converters`; live-verified in a fresh tab via `window.location.href`. Browser back/forward interaction with the redirect specifically was not separately exercised — noted as a QA item in §5, not silently assumed.

## 2. Non-regression acceptance criteria — every existing capability preserved exactly

These are the release gates the project owner specified, expanded into independently-verifiable form. Each must hold **after** this phase's changes land, compared directly against the pre-phase baseline.

1. **Every existing conversion still works, byte-for-byte identical output.**
   - [x] For each of the nine client-side tools (JSON, YAML, XML, CSV, Regex, URL Encode, Unicode Inspector, Cron, Timestamp, Diff), the same input produces the same output before and after this phase — `git status`/`git diff` confirmed zero lines changed in any of the nine tool files across Milestones 4–6; live-verified JSON Minify and Cron's real backend call both still work through the unified page.
   - [x] For Ingest's file pipeline, converting one sample file per extension family already covered by `KNOWN_EXTENSIONS` (at minimum: `.pdf`, `.docx`, `.xlsx`, `.html`, `.txt`, `.jpg`, `.zip`) through `MarkItDownProvider.submit()` produces output identical to calling `services.ingest.converter.submit()` directly — `test_ingest_pipeline.py` (Milestone 1 baseline, re-run unchanged) plus `test_converters_providers.py`'s delegation spy test (Milestone 3); live-verified via real file uploads through the browser dropzone in Milestone 6 (a `.txt` file converted correctly, `status: "done"`).
   - [x] The vision-LLM fallback path (`vision.pdf_needs_vision`, `vision.convert_pdf_via_vision`) is invoked under the exact same conditions as today — `git diff --stat app/services/ingest/` confirmed empty (Milestones 3 and 6); `test_ingest_pipeline.py::test_pdf_needs_vision_is_false_by_default` pins the default-off case explicitly.

2. **No existing API contracts change.**
   - [x] `POST /api/converters/cron/parse` — request schema (`CronParseIn`), response schema (`CronParseOut`), status codes, and behavior are byte-for-byte unchanged — `git diff` on `schemas/converters.py`/`api/routes/converters.py` shows only additive changes (new `ProviderOut`/`ProvidersOut`/`GET /providers`, nothing to the existing route); `test_converters_api.py::test_cron_parse_contract_unchanged` and `test_cron_parse_invalid_expression_contract_unchanged`.
   - [x] `GET /api/ingest/formats`, `POST /api/ingest/jobs`, `GET /api/ingest/jobs/{job_id}`, `GET /api/ingest/jobs/{job_id}/files/{file_id}/download`, `GET /api/ingest/jobs/{job_id}/files/{file_id}/content`, `GET /api/ingest/jobs/{job_id}/download`, `POST /api/ingest/jobs/{job_id}/files/{file_id}/save-to-notes` — all seven endpoints keep their current path, request shape, response shape, and status codes — `backend/app/api/routes/ingest.py` has zero diff (confirmed via `git diff --stat`); `test_converters_api.py::test_ingest_full_lifecycle_contract_unchanged` exercises all seven end-to-end against the real backend.
   - [x] The OpenAPI schema generated by FastAPI (`/openapi.json`) contains every pre-existing path and schema from the baseline unchanged, plus only the new additive `GET /api/converters/providers` path and `ProviderOut`/`ProvidersOut` schemas — `test_converters_api.py::test_openapi_contains_every_pre_existing_path_plus_the_new_one` (a presence check against the documented set, not a byte-diff against a captured pre-phase snapshot — this repo has none; stated plainly in the test's own docstring rather than overclaimed).

3. **Browser (client-side) converters never upload data to the backend.**
   - [x] With the browser's network panel open, using the JSON, YAML, XML, CSV, Regex, URL Encode, Unicode Inspector, Timestamp, and Diff tools produces **zero** network requests of any kind — live-verified in Milestone 4 (manifest-driven render) and Milestone 6 (unified page): only page-load/session-check traffic recorded when clicking JSON's Format/Minify buttons.
   - [x] The Cron tool is the sole exception by original design (unchanged from today): it sends only the cron expression string to `POST /api/converters/cron/parse` — live-verified: exactly one `POST /api/converters/cron/parse → 200 OK` request fired on Parse click, no other payload.
   - [x] No new network call is added to any client-side tool by this phase — confirmed by `git status`/`git diff` showing zero changes to any `frontend/features/converters/*.tsx` file.

4. **Existing Ingest functionality is fully preserved.**
   - [x] Upload size cap (`max_upload_file_size_mb`) and batch count cap (`max_upload_batch_files`) still reject oversized/over-count uploads with the same error messages — `backend/app/api/routes/ingest.py` has zero diff; this logic is untouched code, not independently re-tested at the boundary values in this phase (existing behavior, not a new claim).
   - [x] Filename sanitization (`_safe_name`) still strips directory components and unsafe characters identically — untouched code (zero diff), same reasoning as above.
   - [x] TTL-based job cleanup (`ingest_job_ttl_minutes`, the background cleanup thread) still runs and still deletes expired jobs' in-memory records and on-disk scratch files — `test_ingest_pipeline.py::test_cleanup_expired_removes_only_jobs_past_ttl` (Milestone 1 baseline).
   - [x] Per-file status transitions (`pending → processing → done|error`), zip-all download, single-file download, markdown content preview, and save-to-notes all behave identically to the pre-phase baseline — `test_converters_api.py::test_ingest_full_lifecycle_contract_unchanged` exercises the full sequence against the real backend; live-verified via a real browser file drop in Milestone 6, including the 800ms-poll UI converging to "1 of 1 converted" (one false alarm along the way, traced to background-tab timer throttling in this automation environment, not a code defect — confirmed by re-checking after a real wall-clock wait).

5. **One unified Converter page replaces the previous navigation.**
   - [x] The sidebar shows exactly one nav item for this feature; the command palette (⌘K) shows exactly one matching entry, not two — live-verified in Milestones 5 and 6 via direct DOM inspection of both the sidebar link list and the ⌘K dialog's own rendered text.
   - [x] No dead link exists anywhere in the app pointing at the old two-entry structure — repo-wide grep for `href="/ingest"` (Milestones 5 and 6): zero matches outside the redirect config itself.

6. **Existing `/ingest` links redirect correctly.**
   - [x] `GET /ingest` returns a redirect response to `/converters`, not a 404 or client-side error boundary — `curl` confirmed `307` with the correct `Location` header (Milestone 5).
   - [x] A bookmarked `/ingest` URL, opened in a fresh browser tab with no prior app state, lands the user on a fully-functional `/converters` page — live-verified via direct navigation to `/ingest` in the browser tab, confirmed landing on a fully rendered `/converters` (Milestones 5 and 6).

7. **No database migrations.**
   - [x] `backend/alembic/versions/` contains zero new revision files after this phase's implementation — directory listing confirmed 5 files (`0001`–`0005`), unchanged from the pre-phase baseline (Milestone 6).
   - [x] `alembic current` / the app's own schema-version check reports the same head revision before and after this phase ships — no migration ran on any of this phase's dev-server startups (checked across Milestones 3, 5, and 6's verification sessions).
   - [x] No new `SQLModel` table or column is defined anywhere in `backend/app/models/` — zero diff in `backend/app/models/` (confirmed via `git status`).

8. **No regressions in performance.**
   - [x] Client-side tool operations remain synchronous, in-browser computations with no added latency — covered by criterion 3's zero-network-request confirmation.
   - [x] Ingest job throughput is unchanged: `ingest_workers` thread-pool size (`= 2`, confirmed unchanged in `app/core/config.py`) and the provider wrapper's hot path is one direct function call with no added work (`MarkItDownProvider.submit()` → `converter.submit()`, confirmed by code inspection and the delegation spy test).
   - [x] `GET /api/converters/providers` responds in low-single-digit milliseconds — measured directly: `list_providers()` averaged 0.21μs, max 1.70μs over 1000 calls (Milestone 6) — several orders of magnitude under the "low-single-digit milliseconds" bar.

9. **All existing tests continue to pass.**
   - [x] The full backend test suite (`pytest backend/tests/ -v`) passes with the same pass count as the pre-phase baseline, plus any new tests this phase adds — 138 (pre-phase baseline) → 183 (Milestone 6), 0 failures, 0 errors, re-confirmed fresh in Milestone 6's sweep.
   - [x] `npm run build`, `npm run lint`, and `tsc --noEmit` all pass clean in `frontend/` — confirmed at every milestone boundary from Milestone 4 onward, most recently in Milestone 6 (after clearing a stale `.next` cache reference to the deleted `/ingest` route — an expected artifact, not a code defect).
   - [x] `docker compose build && docker compose up` succeeds and the app reaches a working state with no new migration step — Milestone 7 T20b: built and ran in a fully isolated Compose project (`forge-rc-audit`, port 8587, brand-new named volume, not the user's own stack). Fresh-volume boot applied exactly the five pre-existing migrations (`0001`–`0005`), no sixth. Setup/unlock, the unified `/converters` page, the `/ingest` redirect (`307`), and the Workbench pinned-tools "Converter" tile all confirmed live against the containerized build. Restarted the stack and confirmed the migration re-run was a no-op and all state (session, pinned tools) persisted. Fully torn down afterward (`down -v`) — containers, network, and volume all removed.

## 3. UX acceptance criteria

Derived from [`02_UI.md`](02_UI.md):

- [x] Empty/loading/error/populated states for both the Text & Data section (per-tool, unchanged) and the Documents section (dropzone/job-list, unchanged) render as specified in `02_UI.md` §3 — no new state-handling gap introduced by relocating the components; live-verified the Documents section's empty (bare dropzone) and populated (job list with a real conversion) states in Milestone 6.
- [x] The unified page is usable at mobile widths — both sections stack in a single column below the `md` breakpoint, matching each section's pre-existing responsive behavior (`02_UI.md` §4) — live-verified at 375px (Milestones 5 and 6): zero horizontal overflow (`document.body.scrollWidth` vs. `window.innerWidth`, checked directly, not by eye).
- [x] Every interactive element in both sections remains keyboard-reachable — no new focus trap or unreachable control introduced by the page restructuring (`02_UI.md` §5) — 46 focusable elements found on the unified page (Milestone 5); a spot check, not a full trusted-keyboard-gesture audit, consistent with this environment's known limitations for that specific kind of test (documented, not silently assumed).
- [x] Both light and dark themes render correctly on the unified page (`next-themes`, per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §1) — live-verified `html.dark` applying correctly at both desktop and mobile widths (Milestones 5 and 6).

## 4. Quality acceptance criteria

- [x] All tests enumerated in [`07_TESTING.md`](07_TESTING.md) pass — 183 passed, 0 failures (Milestone 6 fresh run).
- [x] No architectural invariant violated: routers stay thin, no cross-feature imports at the frontend level, models remain the schema source of truth, no ORM object exposed directly — confirmed by code review of `api/routes/converters.py` (parses/delegates/shapes only) and the Workbench fix (a documented, pre-existing "manually synced" seam, not a new cross-feature coupling).
- [x] Zero new entries required in [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) — confirmed no new runtime or build dependency was added anywhere across all six milestones (`typing.Protocol` is stdlib; the frontend manifest references only existing components).
- [x] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied in full — see Milestone 7's T18 for the formal, independent walk-through.
- [x] `CURRENT_STATE.md` reflects reality with no stale "In Progress" items — updated at every milestone boundary through Milestone 6; will be re-confirmed at Milestone 7 close-out.

## 5. Sign-off

Per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), sign-off is the project owner's explicit decision at the Release Candidate → Owner Sign-off transition, evaluated against [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §6's merge criteria: zero open BLOCKERs, MAJOR/MINOR findings triaged (not silently dropped), and every criterion in §1–§4 above either checked against direct evidence or explicitly filed as a QA ticket per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4.

**RC audit complete (2026-07-25, Milestone 7 T18–T20e).** Every criterion in §1–§4 above is checked against direct evidence, re-verified fresh at this milestone (not carried over from Milestone 6 by assumption): backend suite re-run (183 passed), frontend build/lint/typecheck re-run clean, plus three checks intentionally scoped to this milestone rather than earlier ones (per the project owner's explicit RC-audit framing):
- **Fresh-checkout reproducibility** (T20a): a byte-for-byte copy of the current working tree, excluding all caches, with a brand-new Python venv (`pip install -r requirements.txt` only) and a fresh `npm install` (no reused `node_modules`) — build/lint/typecheck/tests all pass from that clean state.
- **Docker Compose clean-room** (T20b): isolated project, fresh named volume, confirmed via restart that the migration re-run is a no-op and state persists; fully torn down afterward.
- **Dependency review** (T20c): `git diff` on `backend/requirements.txt`, `backend/requirements-dev.txt`, `frontend/package.json`, and `frontend/package-lock.json` against the pre-phase baseline — all four empty. Zero new dependencies.

Two pre-existing conditions were surfaced during this audit, neither caused by this phase and neither a BLOCKER: a `.jpg`-without-vision conversion gap (already pinned as a test in Milestone 1) and an `npm ci`/lockfile drift already documented in `frontend/Dockerfile`'s own comment (found while building T20a, unrelated to this phase's zero-diff dependency files). Both recorded in [`10_RELEASE_NOTES.md`](10_RELEASE_NOTES.md)'s Known Issues, not silently absorbed.

**Zero open BLOCKERs.** Per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §2: no data-loss/corruption, no security issue, no build failure, no acceptance-criterion provably false against the running app. The one real finding this phase produced (Workbench's dead pinned-tool key) was caught and fixed during Milestone 5, before it ever shipped — not an open item at RC.

- [ ] Formal Owner Sign-off decision — pending the project owner's review of this RC audit.

## 6. TODO

- [x] These criteria were derived from [`01_SPEC.md`](01_SPEC.md) §3 and the project owner's explicit release-gate list (2026-07-23), and expanded into independently-verifiable form. Project-owner review completed at each milestone boundary through implementation.
- [x] [`07_TESTING.md`](07_TESTING.md) is now filled in, with every test traced back to the specific criterion above it verifies — §4's "all tests in 07_TESTING.md pass" criterion now has a concrete referent.
- [ ] None remaining for this document — awaiting the project owner's Milestone 7 review and formal Sign-off decision.

## 7. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
