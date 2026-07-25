# Universal Converter — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — filled in against [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md), pending project-owner review.
> **Last Updated:** 2026-07-23

---

## 0. A gap this phase must close first

`backend/tests/` today has **zero test coverage** for either Converters (`cron.py`) or Ingest (`converter.py`, `formats.py`, `jobs.py`, `postprocess.py`, `vision.py`) — confirmed by directory listing (only `test_crypto.py`, `test_generators.py`, `test_security.py`, `test_workbench.py`, `test_project_init_*.py`, `test_prompt_studio_*.py` exist). This matters specifically for this phase: [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2's non-regression criteria ("every existing conversion still works," "existing Ingest functionality is fully preserved") are only as meaningful as the tests that pin down today's behavior *before* it gets wrapped. Per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.3 (honest gaps over fake completeness), this plan does not silently rely on "it wasn't tested before either" — §1 below adds baseline/characterization tests for the pre-existing pipeline as part of this phase's own test suite, not as a separate cleanup task. These baseline tests are written first, against the pipeline as it exists **before** the `ConverterProvider` wrapper is added, so they fail honestly if the wrapper ever changes behavior.

## 1. Backend tests

**Baseline/characterization tests — written first, against the unmodified pipeline** (`backend/tests/test_ingest_pipeline.py`, new — flat under `backend/tests/`, matching the existing naming convention):

- `postprocess.clean_markdown`: invisible-character stripping, smart-quote/dash normalization, data-URI-image collapsing, blank-line collapsing — pinned with concrete input/output fixture pairs. Verifies [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2.1.
- `formats.KNOWN_EXTENSIONS`: exact set membership pinned (a snapshot assertion) so any future change to the extension list is a deliberate, visible diff, not a silent drop. Verifies §2.1.
- `jobs.JobStore`: `create()` produces a job with `in`/`out` directories; `Job.status` correctly aggregates `pending`/`processing`/`done`/`error` per-file statuses into the job-level `processing`/`done`/`failed` value; `Job.progress` is `finished/total`; `cleanup_expired()` removes only jobs past the TTL cutoff and deletes their on-disk directories. Verifies §2.4.
- `converter._convert_one` (or an equivalent public entry point): converting one fixture file per extension family (at minimum `.txt`, `.html`, `.docx`, `.xlsx`, `.pdf` without vision, `.jpg`, `.zip`) produces non-empty Markdown output and sets `status == "done"`; an unsupported/corrupt input sets `status == "error"` with a non-empty `task.error`; the upload file is deleted after conversion regardless of outcome (`finally: task.upload_path.unlink`). Verifies §2.1, §2.4.
- `vision.pdf_needs_vision`: returns `False` when `vision_enabled=False` (the default) or `vision_pdf_mode="off"`, regardless of PDF content — the common/default case, pinned explicitly since this is the path nearly every deployment runs. Verifies §2.1 (vision fallback conditions unchanged).

**New capability tests** (`backend/tests/test_converters_providers.py`, new):

- `providers.register()` / `providers.list_providers()`: registering a provider makes it appear exactly once in `list_providers()`; the module-level registration of `MarkItDownProvider` at import time means a fresh import of `app.services.converters.providers` yields exactly one entry with `slug == "markitdown"`, `input_extensions == formats.KNOWN_EXTENSIONS`, `output_format == "markdown"`. Verifies [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1 (`ConverterProvider` exists and is registered).
- `MarkItDownProvider.submit()` delegates to `services.ingest.converter.submit()` with no transformation of its own — verified by asserting the same `Job`/`FileTask` objects passed to `submit()` reach `converter.submit()` unchanged (a spy/monkeypatch on `converter.submit`, asserting call count 1 and identical arguments). Verifies §1 and the "wrap, don't rewrite" design in [`03_BACKEND.md`](03_BACKEND.md) §1.

**Integration tests** (`backend/tests/test_converters_api.py`, new — FastAPI `TestClient`, matching `test_project_init_api.py`'s module-scoped-app-with-isolated-`FORGE_DATA_DIR` pattern):

- `GET /api/converters/providers`: `200` with the one expected provider entry, matching `ProvidersOut`; `401` without a session cookie. Verifies [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1.
- **Contract-preservation tests**, run against the *same* test app both before and after this phase's changes are applied (a diff-based check, not just "still returns 200"):
  - `POST /api/converters/cron/parse` — identical request/response shape and status codes as the pre-phase baseline. Verifies §2.2.
  - `GET /api/ingest/formats`, `POST /api/ingest/jobs` (small `.txt` upload), `GET /api/ingest/jobs/{id}`, `GET /api/ingest/jobs/{id}/files/{id}/content`, `GET /api/ingest/jobs/{id}/files/{id}/download`, `GET /api/ingest/jobs/{id}/download`, `POST /api/ingest/jobs/{id}/files/{id}/save-to-notes` — full lifecycle exercised end-to-end (upload → poll until done → download/preview/save-to-notes), asserting identical status codes and response shapes to the pre-phase baseline. Verifies §2.2 and §2.4.
  - `GET /openapi.json` — every pre-existing path/schema present and unchanged; only the new `GET /api/converters/providers` path and `ProviderOut`/`ProvidersOut` schemas are new. Verifies §2.2's OpenAPI-diff criterion.
- Existing upload-limit/sanitization tests migrated from characterization tests in `test_ingest_pipeline.py` into an API-level check (oversized file → rejected with existing error message; unsafe filename → sanitized) to confirm the behavior survives the full router → provider → service path, not just the service function in isolation. Verifies §2.4.

## 2. Frontend tests

No frontend test framework exists in this codebase (per [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §5 and [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §4, both already noting this as an unresolved TODO). Consistent with Phase 02 and Phase 03's precedent, this phase does not introduce a new frontend test framework unilaterally — that would be a new dependency decision requiring the same "ask first" treatment as any other ([`06_TECH_STACK.md`](../../06_TECH_STACK.md) §4). Frontend correctness is covered by build/lint/typecheck plus the manual verification script in §3.

- [ ] `npm run build` and `npm run lint` clean.
- [ ] `tsc --noEmit` passes.
- [ ] `git diff` of every moved component file (`frontend/features/converters/*.tsx`, `frontend/features/ingest/*.tsx`) shows only import-path/mount-location changes, zero logic diff — the fastest, most direct evidence for [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2.1's "nine tools produce identical output" claim, checked mechanically rather than only by manual re-testing each tool.

## 3. Manual verification

Golden path, run in a real browser against the running app, per [`../../14_IMPLEMENTATION_PLAYBOOK.md`](../../14_IMPLEMENTATION_PLAYBOOK.md) §5. Each step names the [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criterion it verifies.

1. Navigate to the unified page via the sidebar; confirm exactly one nav entry exists for it, and it's also reachable via ⌘K. (§1, §2.5)
2. With the browser's network panel open and recording, use each of JSON, YAML, XML, CSV, Regex, URL Encode, Unicode Inspector, Timestamp, and Diff — confirm **zero** network requests appear for any of them. (§2.3)
3. Use the Cron tool — confirm exactly one request, `POST /api/converters/cron/parse`, carrying only the expression text, no file or document content. (§2.3)
4. Upload a small batch of files (at least one `.pdf`, one `.docx`, one already-known-unsupported extension) via the Documents section's dropzone — confirm per-file progress, a completed job, correct preview content, zip-all download, single-file download, and save-to-notes all work identically to today's Ingest page. (§1, §2.1, §2.4)
5. Attempt an oversized upload and a batch exceeding the file-count cap — confirm the existing rejection messages appear unchanged. (§2.4)
6. Navigate directly to `/ingest` in a fresh tab (no prior app state) — confirm a redirect to `/converters` lands on a fully working page, not a blank/broken intermediate state. (§1, §2.6)
7. Resize to mobile width (375px) — confirm both sections stack in a single column and remain usable. (§3 UX criteria)
8. Toggle dark mode — confirm both sections render correctly. (§3 UX criteria)
9. Tab through both sections using only the keyboard — confirm every control remains reachable (unchanged from today, since no new interactive pattern is introduced). (§3 UX criteria)
10. Run the full backend suite (`pytest backend/tests/ -v`) and confirm the new test count is the pre-phase count plus this phase's additions, with zero failures. (§2.9)
11. `docker compose build && docker compose up` — confirm the app reaches a working state with no migration step logged on startup. (§2.7, §2.9)

## 4. Regression risk

Unlike a wholly new, isolated feature, this phase is **entirely** regression risk by nature — it touches the mount location of every existing Converters and Ingest component and adds a delegation layer in front of the existing Ingest pipeline. The specific risks and their mitigations:

- **Risk:** Moving a tool component (e.g. `json-tool.tsx`) to a new page breaks it via an import-path or prop-wiring mistake. **Mitigation:** §2's diff-based check (zero logic diff expected) plus §3 step 2's manual pass over all nine tools.
- **Risk:** The `MarkItDownProvider` wrapper subtly changes behavior (e.g. swallows an exception, alters a status code, races the job store). **Mitigation:** §1's baseline characterization tests are written against the *unwrapped* pipeline first, then re-run unchanged against the wrapped path in §1's integration tests — any divergence fails loudly rather than passing by omission.
- **Risk:** The `/ingest` → `/converters` redirect breaks a workflow that depended on the old URL directly (e.g. a saved bookmark, an external link in old documentation). **Mitigation:** §3 step 6, plus a repo-wide grep for hardcoded `href="/ingest"` or `"/ingest"` string literals outside the redirect implementation itself, run as part of Milestone 2's own verification (not deferred to RC).
- **Risk:** The new `GET /api/converters/providers` endpoint is accidentally wired with different auth or error-handling than the rest of the app. **Mitigation:** §1's integration test explicitly checks the `401` case, and §1's `AuthDep` usage is copied from the existing `converters.py`/`ingest.py` routers, not reimplemented.
- **Risk:** Existing sidebar/command-palette entries for *other* features (Secrets, Notes, Documents, etc.) get disturbed by editing `nav-registry.ts`. **Mitigation:** the edit is a two-line replacement (delete two entries, add one) in an array — §3 step 1 spot-checks that every other pre-existing nav entry is still present and correctly ordered.

As a final spot-check at Milestone 3 (per [`../../14_IMPLEMENTATION_PLAYBOOK.md`](../../14_IMPLEMENTATION_PLAYBOOK.md) §6's audit guidance): confirm the full existing backend test suite passes alongside this phase's new tests, and that no test file for an unrelated feature (Secrets, Notes, Documents, Generators, Crypto, Utilities, Workbench, Search, Project Init, Prompt Studio, Settings) needed any change.

## 5. TODO

- [ ] Project-owner review of this document alongside [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) — once confirmed, Stage 4 (`09_IMPLEMENTATION_TASKS.md`) can be drafted.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [03_BACKEND.md](03_BACKEND.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../14_IMPLEMENTATION_PLAYBOOK.md](../../14_IMPLEMENTATION_PLAYBOOK.md)
