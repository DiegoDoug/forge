# Universal Converter — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **All seven milestones complete (2026-07-25).** T1–T21 (including T20a–e) all checked off, each approved by the project owner at its milestone boundary. Zero open BLOCKERs. Awaiting the project owner's formal Sign-off decision — see [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §5.
> **Last Updated:** 2026-07-25

---

## 0. Milestone plan

Seven milestones, sequenced per the project owner's explicit ordering (2026-07-23): baseline tests first (so every later milestone has something to be measured against), the backend provider abstraction built and wired before any UI change, the frontend's equivalent abstraction next, then the user-visible consolidation, then hardening, then an independent audit. Each milestone below is scoped so that reverting it alone (via a single revert of its commit(s)) fully restores the previous milestone's state — no milestone depends on a later one existing.

### 0.1 Change-type classification (architectural vs. behavioral)

Per the project owner's authorization rule (2026-07-23): no milestone may introduce both an architectural change and a behavioral change simultaneously unless its own stated objective explicitly requires both. Classified here so compliance is auditable at each milestone-boundary review, not re-derived from prose each time:

| Milestone | Architectural change? | Behavioral change? | Classification |
|---|---|---|---|
| 1 — Baseline characterization tests | No | No | **Neither** — test-only, zero production code touched. |
| 2 — Provider interface and registry | Yes (`ConverterProvider` protocol + registry) | No | **Architecture-only** — proven only against a throwaway fake provider; nothing real consumes it yet, so no observable behavior changes anywhere in the app. |
| 3 — Ingest provider integration | Yes (wires the real pipeline into the registry) | Yes (new endpoint, new caller-visible capability) | **Both — justified.** The milestone's own stated objective is explicitly "wire the real pipeline into the registry ... and expose it over a new endpoint" — the pairing is the point of this milestone, not incidental scope creep. |
| 4 — Browser provider abstraction | Yes (frontend manifest) | No | **Architecture-only** — no live page consumes the manifest yet; every existing tool's behavior is provably unchanged (§ Milestone 4's diff check). |
| 5 — Unified Converter UI and routing | Yes (page composition, routing structure) | Yes (the actual user-visible page/nav/redirect change) | **Both — justified.** The milestone's stated objective is explicitly to ship the unified page, the consolidated nav, and the redirect together — this is the one milestone whose entire purpose is to make the architecture from Milestones 2–4 observable to a real user. |
| 6 — Cleanup, documentation, and regression hardening | No | No (docs + verification; any code removal is confirmed-dead subtraction, not new architecture or new behavior) | **Neither.** |
| 7 — Release candidate audit | No (unless a BLOCKER fix requires one — see below) | Only if a BLOCKER fix requires a behavior correction | **Neither, by default.** If T19's fix for a BLOCKER finding would require *both* an architectural and a behavioral change, that specific fix must stop and be raised to the project owner before proceeding, per [`IMPLEMENT.md`](IMPLEMENT.md) Stop Criteria — it is not pre-authorized by this table. |

Milestones 3 and 5 are the only two where the rule's exception clause applies, and both are called out explicitly in their own **Objective** sections below as requiring the pairing.

### Milestone 1 — Baseline characterization tests

**Objective:** Pin down the current, unmodified behavior of both Converters (`cron.py`) and Ingest (the full MarkItDown pipeline) in tests, before any production code changes. This closes the zero-coverage gap identified in [`07_TESTING.md`](07_TESTING.md) §0 and gives every subsequent milestone something concrete to be verified against — without this milestone, "no regression" in later milestones is an assertion, not a measurement.

**Scope:** New test files only. **Zero production code changes.**

**Files expected to change:**
- `backend/tests/test_converters_cron.py` (new)
- `backend/tests/test_ingest_pipeline.py` (new)

**Implementation tasks:**
- [x] T1 — `test_converters_cron.py`: pin `parse_cron`'s current behavior — valid expression → description format + exact `next_runs` count; invalid expression → the existing `AppError` message. This is net-new coverage; `cron.py` has shipped with zero tests until now.
- [x] T2 — `test_ingest_pipeline.py` part A: `postprocess.clean_markdown` (invisible-char stripping, smart-quote/dash normalization, data-URI collapsing, blank-line collapsing — concrete fixture pairs); `formats.KNOWN_EXTENSIONS` (snapshot assertion); `jobs.JobStore` (`create`, `Job.status` aggregation, `Job.progress`, `cleanup_expired`).
- [x] T3 — `test_ingest_pipeline.py` part B: `converter._convert_one` (or its current public entry point) across one fixture file per extension family (`.txt`, `.html`, `.docx`, `.xlsx`, `.pdf` with vision disabled, `.jpg`, `.zip`) plus the error path (corrupt/unsupported input → `status == "error"`, non-empty `task.error`, upload file still deleted); `vision.pdf_needs_vision` pinned to `False` under the default (`vision_enabled=False`) configuration.

**Dependencies:** None — this milestone touches no production code and can start immediately.

**Acceptance criteria:** Traces to [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2.1/§2.4's underlying claims — these tests *are* the mechanism that makes those claims falsifiable in later milestones, not something this milestone itself is graded against (nothing has changed yet). Concretely: all new tests pass against the current, untouched codebase; `pytest backend/tests/ -v` shows the pre-existing pass count plus these new tests, zero pre-existing test affected.

**Tests to execute:** The new tests themselves; the full existing suite (to confirm zero interference from adding new test files).

**Rollback considerations:** Trivial — delete the two new test files. No production code is touched, so there is no blast radius beyond the tests themselves.

**Estimated complexity:** **S** — test-writing against already-understood, already-working code; no new abstractions.

**✅ Milestone 1 complete (2026-07-23).** 27 new tests, all green: 6 in `test_converters_cron.py` (T1), 21 in `test_ingest_pipeline.py` (T2 postprocess/formats/jobs + T3 converter/vision). Full suite: 138 → 165 passed, 0 failures, 0 errors, 0 pre-existing test affected.

Real, observed behavior pinned (verified by actually running the code, not assumed) — kept here as the record future milestones are checked against:
- `postprocess.clean_markdown`: invisible-char stripping, smart-quote/dash normalization, long-data-URI collapsing (≥64 chars after `data:`), multi-blank-line collapsing outside code fences, and blank-line *preservation* inside fenced code blocks — all confirmed via direct probe before being written as assertions.
- `formats.KNOWN_EXTENSIONS`: 39-extension snapshot pinned exactly.
- `jobs.JobStore`/`Job`: status aggregation (`"done"` when any mix of done/error, `"failed"` only when *every* file errored, `"processing"` otherwise), progress as finished/total, TTL-based `cleanup_expired` removing only expired jobs' records and on-disk directories.
- `converter._convert_one` real conversions (not mocked) for `.txt`, `.html`, `.docx`, `.xlsx`, `.pdf` (vision disabled), `.zip` (recurses into contents) — all `status == "done"` with the expected Markdown shape.
- **A real, pre-existing gap confirmed and pinned, not fixed (out of this milestone's scope):** a `.jpg` with no caption-worthy text and vision disabled converts to `status == "error"` ("Conversion produced no text content") — today's actual behavior for any image upload without vision assistance configured. This is exactly the kind of gap [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) §1.3 says to track honestly rather than silently paper over; it is unchanged by this phase (no new conversion direction is in scope per [`01_SPEC.md`](01_SPEC.md) §5) and is now a pinned, visible test rather than an undocumented surprise.
- `vision.pdf_needs_vision` confirmed `False` under the default (`vision_enabled=False`) configuration, regardless of PDF content.

Isolation notes: the `JobStore`/`Job`-dir tests use a per-test fake settings object patched via `monkeypatch` (not the module's real global `store` singleton and not the shared `FORGE_DATA_DIR`), so nothing here can collide with another test module or leave scratch data behind — `pytest`'s `tmp_path` handles cleanup automatically.

**Per the change-type rule (§0.1): Milestone 1 introduced zero architectural change and zero behavioral change** — test-only, as classified.

Zero production code was touched. Ready for project-owner review per the milestone-boundary cadence — Milestone 2 has not started.

---

### Milestone 2 — Provider interface and registry

**Objective:** Introduce the `ConverterProvider` protocol and a minimal registry (per [`03_BACKEND.md`](03_BACKEND.md) §2), proven with a throwaway test-only provider — **not yet wired to the real Ingest pipeline**. Separating this from Milestone 3 means the abstraction itself is verified in complete isolation before anything real depends on it.

**Scope:** New backend module only. No existing service, route, or schema is touched.

**Files expected to change:**
- `backend/app/services/converters/providers/__init__.py` (new)
- `backend/tests/test_converters_providers.py` (new)

**Implementation tasks:**
- [x] T4 — `providers/__init__.py`: `ConverterProvider` `Protocol` (`slug`, `label`, `input_extensions`, `output_format`, `submit(job)`), `register()`, `list_providers()`, per [`03_BACKEND.md`](03_BACKEND.md) §2's exact shape.
- [x] T5 — `test_converters_providers.py` (registry-only tests): a fake/dummy provider defined inline in the test file registers and appears exactly once in `list_providers()`; registering two providers preserves both; the registry has zero import-time dependency on `services.ingest` at this point (confirmed by the test file itself not importing it).

**Dependencies:** None strictly (this is new, self-contained code) — sequenced after Milestone 1 per the owner's ordering so the baseline exists before any new abstraction is introduced, not because the code requires it.

**Acceptance criteria:** Traces to [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1's "`ConverterProvider` protocol exists ... with `register()`/`list_providers()`" — verified here against a fake provider only; the real-provider half of that criterion is Milestone 3's.

**Tests to execute:** `pytest backend/tests/test_converters_providers.py -v`; full existing suite (including Milestone 1's new tests) to confirm zero interference.

**Rollback considerations:** Delete the new `providers/` submodule and its test file. Nothing else in the codebase references it yet — zero blast radius.

**Estimated complexity:** **S** — a `Protocol` and a list, no I/O, no external dependency.

**✅ Milestone 2 complete (2026-07-25).** `providers/__init__.py` implements `ConverterProvider` (a `runtime_checkable` `Protocol`: `slug`, `label`, `input_extensions`, `output_format`, `submit(job)`), module-level `_PROVIDERS` list, `register()`, `list_providers()` — matching [`03_BACKEND.md`](03_BACKEND.md) §2's shape exactly. `submit`'s `job` parameter is deliberately left untyped (no `Job` import) so this module has zero dependency on `services.ingest` or any other concrete pipeline at this stage.

7 new tests in `test_converters_providers.py`, all against a throwaway `_FakeProvider` defined in the test file itself (never a real provider): empty-registry start, single/multiple registration, `list_providers()` returns a defensive copy (mutating the returned list doesn't affect the live registry), protocol conformance (`isinstance(fake, ConverterProvider)` via `runtime_checkable`), and that the registry itself never calls `submit` (only a caller does). An `autouse` fixture resets `providers._PROVIDERS` to an empty list before every test, so these tests can't leak state into each other or into Milestone 3's future extension of this same file.

**Verified, not assumed:** an AST-level check of `providers/__init__.py` confirms its only two imports are `__future__` and `typing` — zero coupling to `services.ingest`, satisfying this milestone's architecture-only classification (§0.1) directly, not just by convention. Full suite: 165 → 172 passed, 0 failures, 0 errors — the 7 new tests, zero regressions.

**Per the change-type rule (§0.1): Milestone 2 introduced an architectural change (the protocol/registry) and zero behavioral change** — nothing in the running app calls `register()` with a real provider yet, so no observable behavior anywhere changed. Ready for project-owner review; Milestone 3 has not started.

---

### Milestone 3 — Ingest provider integration

**Objective:** Wire the existing, unmodified Ingest pipeline into the registry from Milestone 2 via a thin `MarkItDownProvider` adapter (per [`03_BACKEND.md`](03_BACKEND.md) §1–§2 — delegation, not rewrite), and expose the registry over the new additive `GET /api/converters/providers` endpoint.

**Scope:** One new adapter module, one new schema pair, one new route. `services/ingest/` itself is not modified — this is the milestone where the "wrap, don't rewrite" design gets proven, not just asserted.

**Files expected to change:**
- `backend/app/services/converters/providers/markitdown.py` (new)
- `backend/app/schemas/converters.py` (add `ProviderOut`, `ProvidersOut`)
- `backend/app/api/routes/converters.py` (add `GET /providers`)
- `backend/tests/test_converters_providers.py` (extend)
- `backend/tests/test_converters_api.py` (new)

**Implementation tasks:**
- [x] T6 — `providers/markitdown.py`: `MarkItDownProvider` (`slug="markitdown"`, `input_extensions=formats.KNOWN_EXTENSIONS`, `output_format="markdown"`, `submit()` delegating directly to `services.ingest.converter.submit`); registered at module import time.
- [x] T7 — `schemas/converters.py`: `ProviderOut`/`ProvidersOut`; `api/routes/converters.py`: `GET /providers` returning `providers.list_providers()` shaped through the new schema, `AuthDep`-gated like every other route in that file.
- [x] T8 — Test pass: extend `test_converters_providers.py` with a delegation/spy test (`MarkItDownProvider.submit()` calls `converter.submit()` exactly once with the same arguments, no transformation); new `test_converters_api.py` covers the new endpoint (`200` + shape, `401` without session) **and** the full contract-preservation suite from [`07_TESTING.md`](07_TESTING.md) §1 (every existing `/api/ingest/*` endpoint and `/api/converters/cron/parse` exercised end-to-end; `GET /openapi.json` checked to confirm only additive changes). Milestone 1's baseline tests are re-run here, unchanged, and must still pass — that's the direct proof this milestone didn't alter existing behavior.

**Dependencies:** Milestone 1 (baseline tests must exist to diff against) and Milestone 2 (the protocol/registry this milestone wires into).

**Acceptance criteria:** [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1 (provider registered with real data, endpoint works) and §2.2 (every existing endpoint's contract unchanged, verified by diff, not just "still returns 200").

**Tests to execute:** `pytest backend/tests/test_converters_providers.py backend/tests/test_converters_api.py -v`; Milestone 1's baseline tests, unchanged; full existing suite.

**Rollback considerations:** Revert `providers/markitdown.py` and the schema/route additions. `services/ingest/` was never modified, so Ingest's actual behavior is unaffected by this revert either way — the rollback is purely subtractive (remove the new wrapper and endpoint), with no risk of leaving Ingest in a partially-migrated state.

**Estimated complexity:** **M** — the first milestone touching a real, already-working pipeline, even though only additively.

**✅ Milestone 3 complete (2026-07-25).** `providers/markitdown.py` (new): `MarkItDownProvider`, a pure delegation adapter — `submit()` forwards directly to `services.ingest.converter.submit`, no transformation. `schemas/converters.py` gained `ProviderOut`/`ProvidersOut`; `api/routes/converters.py` gained `GET /providers`, `AuthDep`-gated identically to the existing `cron/parse` route, importing `providers.markitdown` for its registration side effect.

11 new tests: 2 extending `test_converters_providers.py` (the real `MarkItDownProvider`'s declared shape, and a monkeypatch-spy proof that `submit()` delegates to `converter.submit()` exactly once with the unmodified job object) and 9 in new `test_converters_api.py` (the new endpoint's `200`/`401`, full `cron/parse` contract, full Ingest lifecycle — upload → poll → content → download → zip-all → save-to-notes — an OpenAPI presence check for every pre-existing path plus the new one, and an explicit no-session-cookie check on `/api/ingest/formats`).

Confirmed, not assumed: `git diff --stat app/services/ingest/` is empty — zero lines changed in the wrapped pipeline. Milestone 1's baseline tests re-ran unchanged and green as part of the full suite. Full suite: 172 → 183 passed, 0 failures, 0 errors.

**Two real issues found and fixed during this milestone, worth recording plainly:**
1. **A genuine test-isolation bug in this milestone's own test design**, not production code: the first version of the two new `test_converters_providers.py` tests imported `providers.markitdown` lazily inside the test function body. Because that file's Milestone-2 `isolated_registry` autouse fixture patches `_PROVIDERS` to a fresh empty list for *every* test in the file, the one-time, process-wide `register(MarkItDownProvider())` side effect (which only ever runs on a module's *first* import) fired while `_PROVIDERS` was patched to a throwaway list — and was silently discarded when the fixture reverted at teardown. The real endpoint then reported zero providers. Fixed by moving the `markitdown` import to module level (executed once at collection time, before any fixture runs) — verified robust by re-running the two Milestone-3 test files in every collection order (`api`-then-`providers`, `providers`-then-`api`, each alone) with all passing.
2. **A platform-specific newline-translation detail in the pre-existing, unmodified `converter.py`**: `out_path.write_text(markdown, encoding="utf-8")` uses Python's default text-mode newline translation, which is a no-op on Linux (the real deployment target) but converts `\n` → `\r\n` on Windows dev environments. This surfaced only because `test_converters_api.py`'s download test reads raw HTTP response bytes rather than text-mode content (unlike Milestone 1's tests, which read via `.read_text()` and so never saw it). This is pre-existing, unmodified behavior — not a regression from this milestone — so the test was adjusted to normalize line endings before comparing, with a comment explaining why, rather than "fixing" pipeline code that is explicitly out of this phase's scope.

**Per the change-type rule (§0.1): Milestone 3 introduced both an architectural change (wiring the real provider into the registry) and a behavioral change (the new endpoint) — exactly as pre-authorized by this milestone's own stated objective**, the one place besides Milestone 5 where that pairing is expected rather than a violation. Ready for project-owner review; Milestone 4 has not started.

---

### Milestone 4 — Browser provider abstraction

**Objective:** Give the nine client-side text/data tools a declarative, provider-shaped manifest (slug/label/description/component) — a frontend-only organizational construct, **not** a change in execution location (per the confirmed decision in [`01_SPEC.md`](01_SPEC.md) §1 that these tools stay client-side). This is what lets Milestone 5's unified page render the "Text & Data" section from a manifest instead of a hardcoded JSX list, mirroring the backend registry's shape conceptually without moving any computation to the server.

**Scope:** One new frontend manifest file. **Zero changes to any of the nine existing tool components.**

**Files expected to change:**
- `frontend/features/converters/providers.ts` (new)

**Implementation tasks:**
- [x] T9 — `providers.ts`: an array of `{ slug, label, description, Component }` for the nine existing tools (`JsonTool`, `YamlTool`, `XmlTool`, `CsvTool`, `RegexTool`, `UrlEncodeTool`/`UnicodeInspector`, `CronTool`, `TimestampTool`, `DiffTool`), importing each component unmodified from its existing file.
- [x] T10 — Verification: `git diff` of every existing tool file shows zero lines changed (only the new manifest file is added); a throwaway local render of the manifest (e.g. a temporary test page, removed before Milestone 5 builds the real one) confirms all nine tools render and behave identically to today.

**Dependencies:** None on Milestones 2–3 (frontend-only, independent of the backend provider work) — sequenced here per the owner's ordering to keep "backend abstraction" and "frontend abstraction" as cleanly separable concerns before they're composed in Milestone 5.

**Acceptance criteria:** [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2.1/§2.3 — no tool's behavior or network profile changes; the manifest lists exactly nine entries matching today's tool set.

**Tests to execute:** `npm run build`, `npm run lint`, `tsc --noEmit`; the git-diff check in T10; a manual smoke pass of all nine tools via the manifest-driven render.

**Rollback considerations:** Delete `providers.ts`. Nothing in the live app consumes it until Milestone 5, so this is zero-risk to revert on its own.

**Estimated complexity:** **S** — a data manifest referencing existing components, no new logic.

**✅ Milestone 4 complete (2026-07-25).** `frontend/features/converters/providers.ts` (new): `CONVERTER_TOOL_PROVIDERS`, an array of `{slug, label, description, Component}`. One correction to this section's own wording, caught while building it: there are **nine tool files but ten rendered components** — `url-unicode-tool.tsx` exports two (`UrlEncodeTool` and `UnicodeInspector`), both already rendered as separate cards on today's `/converters` page. The manifest has ten entries, matching today's page exactly; "nine tools" above was shorthand for "nine files," not a literal component count.

Verified, not assumed: `git status --short frontend/features/converters/` shows only the new file — zero lines changed in any of the nine existing tool files. `tsc --noEmit`, `npm run lint`, and `npm run build` all clean, both before and after the throwaway verification page below was added and removed.

Built a throwaway page (`frontend/app/(app)/m4-smoke-test/page.tsx`) that renders `CONVERTER_TOOL_PROVIDERS.map(({slug, Component}) => <Component key={slug} />)`, started the project's `backend-verify`/`frontend-verify` dev servers (isolated from any real running instance, per `.claude/launch.json`), completed first-run setup, and compared `/converters` (unmodified) against `/m4-smoke-test` (manifest-driven) side by side: identical content, identical order, for all ten tools. Went beyond a static-text comparison to confirm real interactivity survived the indirection — clicked JSON's Minify button (produced the correct minified output) and clicked Cron's Parse button, confirming a real `POST /api/converters/cron/parse` → `200 OK` network call fired and its response rendered, through a component reached only via the manifest. Removed the throwaway page and scratch dev-data afterward; re-confirmed `tsc`/`lint` clean with it gone.

**Per the change-type rule (§0.1): Milestone 4 introduced an architectural change (the manifest) and zero behavioral change** — nothing in the live app consumes `providers.ts` yet (the throwaway verification page was deleted, not shipped), so no real user-facing behavior changed. Ready for project-owner review; Milestone 5 has not started.

---

### Milestone 5 — Unified Converter UI and routing

**Objective:** Ship the single `/converters` page (Text & Data + Documents sections), consolidate the nav-registry entry, and redirect `/ingest` — the first milestone with user-visible change, per [`02_UI.md`](02_UI.md).

**Scope:** Page composition, routing, and nav-registry only. No tool logic, no Ingest pipeline logic.

**Files expected to change:**
- `frontend/app/(app)/converters/page.tsx` (rewritten — renders "Text & Data" from Milestone 4's `providers.ts` manifest, and "Documents" from the existing, unmodified `Dropzone`/`JobList`/`PreviewSheet` components)
- `frontend/app/(app)/ingest/page.tsx` (replaced with a redirect, or removed in favor of a `next.config.ts` `redirects()` entry — decided during implementation, whichever is the more standard Next.js App Router pattern for a permanent internal redirect)
- `frontend/lib/nav-registry.ts` (two entries → one, per [`02_UI.md`](02_UI.md) §2)

**Files actually changed** (two more than planned — see the Workbench finding in the completion note below):
- `frontend/app/(app)/converters/page.tsx` (rewritten, as planned)
- `frontend/app/(app)/ingest/page.tsx` (deleted; redirect handled centrally in `next.config.ts` instead of a per-route redirect page)
- `frontend/next.config.ts` (added the `/ingest` → `/converters` redirect entry, following the existing `/vault` → `/secrets` precedent exactly)
- `frontend/lib/nav-registry.ts` (as planned)
- `backend/app/services/workbench.py`, `frontend/features/workbench/tool-metadata.ts`, `backend/tests/test_workbench.py` (**not originally planned** — see below)

**Implementation tasks:**
- [x] T11 — Rewrite `converters/page.tsx` to render both sections; Documents-section components are imported unmodified from `frontend/features/ingest/`.
- [x] T12 — `/ingest` → `/converters` redirect (no 404, no blank intermediate state); confirm the redirect preserves any query string a deep link might have carried, if applicable.
- [x] T13 — `nav-registry.ts`: replace the two existing entries with the single consolidated entry per [`02_UI.md`](02_UI.md) §2.
- [x] T14 — Manual verification: [`07_TESTING.md`](07_TESTING.md) §3 steps 1, 2, 3, 6, 7, 8, 9 (nav/palette count, zero-upload check for the nine tools, Cron's single expression-only call, the `/ingest` redirect in a fresh tab, mobile width, dark mode, keyboard tab-through); a repo-wide grep for any remaining hardcoded `href="/ingest"` outside the redirect itself.

**Dependencies:** Milestone 3 (the backend `GET /api/converters/providers` endpoint exists, even if this milestone's UI doesn't strictly require calling it — the Documents section could optionally use it to render its supported-format list, per [`01_SPEC.md`](01_SPEC.md) requirement 7) and Milestone 4 (the frontend manifest this page renders from).

**Acceptance criteria:** [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1 (unified page, single nav entry), §2.5 (unified nav replaces the two old entries), §2.6 (`/ingest` redirects correctly), §3 (UX states/responsive/keyboard/theme all carry over unchanged).

**Tests to execute:** The manual script in T14 above; `npm run build`/`lint`/`tsc --noEmit`.

**Rollback considerations:** This is the milestone with the most user-visible surface, but the rollback is still a straightforward revert: restoring the previous two-page `converters/page.tsx` + real `ingest/page.tsx` + two-entry `nav-registry.ts` from the prior commit. No data loss risk (this milestone touches no persistence), and Milestones 1–4's backend/manifest work remains valid and unaffected either way.

**Estimated complexity:** **M** — UI composition and routing change with real user-visible surface, but no backend or data risk.

**✅ Milestone 5 complete (2026-07-25).** `converters/page.tsx` rewritten to render "Text & Data" (from Milestone 4's `CONVERTER_TOOL_PROVIDERS` manifest) and "Documents" (the unmodified Ingest dropzone/job-list/preview-sheet components) as two sections. `/ingest` retired: its `page.tsx` deleted, and `next.config.ts` gained a `redirects()` entry (`permanent: false`, following the existing `/vault` → `/secrets` alias's exact precedent and reasoning — a redirect is easier to adjust than to undo). `nav-registry.ts`'s two entries collapsed into one (`"Converter"`, `/converters`, keeping the `Repeat` icon and `O` shortcut).

**A real, unplanned cross-feature dependency was found and fixed, not glossed over.** Workbench (Phase 01, released and frozen) has its own "manually synced" mapping from nav-registry hrefs to pinned-tool metadata (`frontend/features/workbench/tool-metadata.ts`'s own comment already documents this seam explicitly). It also carried `"ingest"` as a `WORKBENCH_TOOL_KEYS` entry and — notably — as the **first item in `DEFAULT_PINNED_TOOLS`**, meaning every fresh Forge install pins "Ingest" by default. It further carried a forward-looking `"universal_converter": {"available": False}` placeholder, clearly anticipating this exact phase (mirroring the `prompt_studio` placeholder Phase 03 flipped on shipping). Removing `/ingest` from `nav-registry.ts` without addressing this would have silently dropped the default-pinned "Ingest" tile from every user's Workbench (`pinned-tools-panel.tsx`'s `metadataMap[tool.key]` lookup fails softly to `null` → renders nothing, not a crash — so this would have been a quiet regression, not a loud one).

Fixed by retiring both the dead `"ingest"` key and the now-redundant `"universal_converter"` placeholder in favor of the single `"converters"` key (unchanged, already available, already correctly mapped) — since this phase's actual design unified the two pages into one, there is no longer a meaningful distinction between "the Converters tool" and "the anticipated Universal Converter tool" to keep as two separate pinnable tiles:
- `backend/app/services/workbench.py`: removed `"ingest"` and `"universal_converter"` from `WORKBENCH_TOOL_KEYS`; `DEFAULT_PINNED_TOOLS` changed from `["ingest", "notes", "prompt_studio", "universal_converter", "secrets", "search"]` (6 items) to `["converters", "notes", "prompt_studio", "secrets", "search"]` (5 items) — both dead/placeholder entries collapsed into the one real entry that now covers their intent.
- `frontend/features/workbench/tool-metadata.ts`: removed the dead `"/ingest": "ingest"` mapping and the retired `universal_converter` `EXTRA_TOOL_METADATA` entry (and its now-unused `Repeat` icon import).
- `backend/tests/test_workbench.py`: one pre-existing test (`test_reset_layout_restores_the_default_layout`) hardcoded the pinned-tools count as a literal `== 6` *in addition to* comparing against the `DEFAULT_PINNED_TOOLS` constant symbolically — updated to `== 5` with a comment explaining why, since the symbolic comparison alone doesn't catch a stale literal.

This is treated as in-scope maintenance of an already-documented "manually synced" seam directly caused by this phase's own nav change, not new Workbench feature work — the same judgment call and precedent Phase 03 recorded for flipping its own forward-looking placeholder. Per [`09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3, this is a "fix a bug in code being actively touched, clearly in-scope and low-risk" — proceeded without a separate stop-and-ask, but documented in full here and flagged plainly in this note rather than silently folded in.

**Verified, not assumed:** full backend suite (183 passed, 0 failures — the one test-literal fix above is the only change to an existing test); `tsc --noEmit`/`npm run lint`/`npm run build` all clean (after clearing a stale `.next` build-cache reference to the deleted `/ingest` route, itself expected and not a code defect). Live-verified against the project's isolated `backend-verify`/`frontend-verify` servers (not the user's own instance): sidebar shows exactly one "Converter" entry; command palette (⌘K) lists exactly one "Converter" (shortcut `O`), no "Ingest"; **the Workbench pinned-tools panel correctly shows a "Converter" tile with no missing/broken tile** — direct, positive confirmation the fix above works, not just an absence of errors; `/ingest` navigated in a fresh tab lands on a fully working `/converters`, confirmed via both `window.location.href` and a raw `curl` check showing `307` with the correct `Location`; zero network requests fired from clicking the JSON tool's Format button (only page-load/session-check traffic); no horizontal overflow at 375px; dark mode applies (`html.dark`); 46 focusable elements found on the unified page (keyboard-reachability spot check, not a full audit — matching this environment's known limitations for real keyboard-gesture testing, documented rather than silently assumed).

**Per the change-type rule (§0.1): Milestone 5 introduced both an architectural change (page composition, routing structure, the Workbench mapping fix) and a behavioral change (the actual unified page, nav consolidation, and redirect) — exactly the pairing pre-authorized by this milestone's own stated objective.** The Workbench fix is classified the same way: it's a direct, necessary consequence of shipping the nav consolidation this milestone's objective already covers, not a separate, unauthorized architectural change layered on top.

Ready for project-owner review; Milestone 6 has not started.

---

### Milestone 6 — Cleanup, documentation, and regression hardening

**Objective:** Run the full [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2 non-regression suite end-to-end (not per-milestone slices), update the shipped-app docs to describe the new unified surface, and confirm no dead code was left behind by the consolidation.

**Scope:** Documentation and verification. Any code change here is subtractive (removing confirmed-unreferenced leftovers) or a fix for something the full-suite pass surfaces — not new capability.

**Files expected to change:**
- `docs/Architecture.md`, `docs/API.md`, `docs/FolderStructure.md` (reflect the unified surface, the new endpoint, the retired `/ingest` route)
- Root `README.md` (feature list wording, if "Converters" and "Ingest" are listed separately today)
- `forge-docs/02_ROADMAP.md` (Phase 04 status)
- Any file confirmed unreferenced after the Milestone 5 consolidation (verified before removal, not assumed)

**Implementation tasks:**
- [x] T15 — Full regression sweep: every [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2 criterion re-checked together in one pass (not milestone-by-milestone), including the full backend suite, `npm run build`/`lint`/`tsc --noEmit`, and the complete manual golden path from [`07_TESTING.md`](07_TESTING.md) §3.
- [x] T16 — Documentation updates listed above.
- [x] T17 — Dead-code check: confirm (via grep/import-graph, not assumption) whether anything from the old two-page structure is now unreferenced, and remove only what's confirmed dead.

**Dependencies:** Milestones 1–5 complete.

**Acceptance criteria:** Every criterion in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1–§4 checked against direct evidence at least once, end-to-end, in this milestone (individual milestones above verify their own slice; this is the integration check across all of them together).

**Tests to execute:** Full backend suite; full frontend build/lint/typecheck; full manual golden path; documentation cross-reference check (no broken links introduced).

**Rollback considerations:** Documentation changes are trivially revertable (no code risk). Any dead-code removal is preceded by a confirm-unreferenced check specifically so it's safe to revert (nothing else depends on what's removed) — if T17 turns up something ambiguous, it's left in place rather than guessed at.

**Estimated complexity:** **S–M** — mostly verification and documentation; low code risk.

**✅ Milestone 6 complete (2026-07-25).**

**T15 (full regression sweep):** Backend suite re-run fresh: 183 passed, 0 failures. Confirmed `alembic/versions/` still holds exactly 5 files (`0001`–`0005`) and `git diff --stat app/services/ingest/ app/services/converters/cron.py` is empty. Measured `list_providers()` directly (1000 calls, avg 0.21μs, max 1.70μs) rather than asserting its triviality from code reading alone. Ran a complete, continuous manual golden path against the isolated `backend-verify`/`frontend-verify` servers — the first time all of it happened in one session rather than split across milestones: unified page render, sidebar/⌘K single-entry check, a **real file drop through the dropzone's file input** (dispatched via a synthetic `DataTransfer`/`change` event, not just an API-level test), the job polling to completion, mobile width + dark mode together (not just separately, as in earlier milestones), and a keyboard-reachability spot check.

One thing worth recording plainly: the live upload initially appeared stuck at "0 of 1 converted" even though a direct API check showed the job as `"done"`. Investigated rather than dismissed — traced to this automation environment's background-tab timer throttling delaying the 800ms `refetchInterval` poll, not a code defect: waiting a real few seconds (not a rapid tool-call retry) let it converge correctly to "1 of 1 converted," and a second upload attempt confirmed the same convergence. Separately, one self-inflicted mistake during this pass: a too-broad button selector clicked the topbar's "Lock" button instead of the job list's preview icon, locking the session — caught immediately (the app correctly returned to the unlock screen, no crash), not a defect in the app.

**T16 (documentation):** Updated `docs/Architecture.md` (renamed the "Ingest" section to "Converter," describing the unification and the new provider registry), `docs/API.md` (the `/api/converters` and `/api/ingest` endpoint-group rows), `docs/FolderStructure.md` (noted the new `providers/` submodule), root `README.md` (collapsed the separate "Converters" and "Ingest" bullets into one "Converter" bullet, updated the intro sentence), and `forge-docs/02_ROADMAP.md` (Phase 04's status row and the document's own header, both were stale at "Not started").

**T17 (dead-code check):** Repo-wide grep for `href="/ingest"`, stale `"Ingest"` nav references, and leftover `m4-smoke-test`/`m6-sweep` artifacts — all clean. The only git-tracked change touching the old route is its deletion. Confirmed the two remaining `"ingest"`/`"universal_converter"` string matches in `backend/app/services/workbench.py` are the explanatory comments left from Milestone 5's fix, not live code.

**Per the change-type rule (§0.1): Milestone 6 introduced neither an architectural nor a behavioral change** — verification, documentation, and a dead-code check that found nothing to remove, as expected for this milestone's classification.

Ready for project-owner review; Milestone 7 (Release candidate audit) has not started.

---

### Milestone 7 — Release candidate audit

**Objective:** An independent RC audit pass per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) — verify every [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criterion against direct evidence (not "looks done"), classify any findings per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md), fix any BLOCKER on the spot, and prepare the phase for project-owner sign-off. **Per the project owner's explicit framing at authorization (2026-07-25): this milestone audits things intentionally *not* exercised during implementation** — fresh-checkout reproducibility, a from-scratch build/lint/typecheck, dependency review, repository cleanliness, release-notes/changelog consistency, and confirmation that Milestones 1–6's acceptance evidence still matches HEAD — not another round of feature verification.

**Scope:** Verification and, if needed, targeted bug fixes only. No new capability.

**Amendment (2026-07-25, project owner):** added **T20a — fresh-checkout reproducibility check** ahead of the Docker check, specifically requested as a distinct step: clone/checkout HEAD into an isolated directory, install every dependency from lockfiles only (`npm ci`, a brand-new Python venv via `pip install -r requirements.txt`) with zero reliance on this session's existing `node_modules`/`.venv`, and confirm the documented commands produce a working build. The owner's rationale: this catches issues incremental development environments hide (an incidental global package, a stale cache masking a missing pin) that even a Docker build can mask if BuildKit cache mounts are in play. The original T20 (Docker Compose) is renumbered T20b below; both are distinct checks, not redundant with each other.

**Files expected to change:**
- `08_ACCEPTANCE.md` (criteria checked off with evidence, matching the rigor of Phase 03's T17 pass)
- `CURRENT_STATE.md` (updated to reflect RC-audit-complete status)
- `history/Phase-04/BUGS/` (new, only if a finding requires tracking, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §5)
- Any file touched by a BLOCKER fix, if one is found

**Implementation tasks:**
- [x] T18 — Walk [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1–§4 line by line; check each against a specific test name, live browser action, or code-review point (not assumed from the implementation existing) — matching the rigor of Phase 03's T17 pass. Re-run backend suite and frontend build/lint/tsc fresh (not carried over from Milestone 6) to confirm evidence matches current HEAD.
- [x] T19 — Classify and fix any finding per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §2 (BLOCKER fixed immediately, re-enter RC per RC1→RC2 if needed; MAJOR/MINOR triaged, not silently dropped).
- [x] T20a — Fresh-checkout reproducibility check (added per project-owner amendment above): a clean git worktree/checkout of HEAD, `npm ci` from `package-lock.json` only, a brand-new Python venv with `pip install -r requirements.txt` only, confirm build/lint/typecheck/tests all pass with zero dependency on this session's pre-existing `node_modules`/`.venv`.
- [x] T20b — Full-stack clean-room verification: `docker compose build && docker compose up` in an isolated Compose project (matching Phase 03's T16 precedent — not the user's own running stack), confirm no migration step runs beyond the expected schema-version check (per [`04_DATABASE.md`](04_DATABASE.md)), and re-run the complete golden path against the containerized build.
- [x] T20c — Final dependency review: diff `backend/requirements.txt` and `frontend/package.json` against the pre-phase baseline, confirm zero unexpected additions (per [`01_SPEC.md`](01_SPEC.md) requirement 9 and [`06_TECH_STACK.md`](../../06_TECH_STACK.md) §4).
- [x] T20d — Repository cleanliness: confirm no generated artifacts, temp files, or stale scratch data (verification server data dirs, throwaway pages) were left committed.
- [x] T20e — Release-notes/changelog consistency: confirm whether this repo has a release-notes convention this phase needs to produce or update (per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §5's `10_RELEASE_NOTES.md`), consistent with Phase 01–03's precedent.
- [x] T21 — Close-out: `CURRENT_STATE.md` reflects reality with no stale "in progress" items; final checkpoint produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md); phase ready for Owner Sign-off per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md).

**Dependencies:** Milestone 6 complete.

**Acceptance criteria:** Zero open BLOCKERs; every [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criterion either checked with cited evidence or explicitly filed as a QA ticket per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4.

**Tests to execute:** The complete test suite (backend + frontend); the Docker Compose clean-room build/up/golden-path in T20; a final full manual pass of every acceptance criterion.

**Rollback considerations:** If a BLOCKER is found, the fix-forward path (RC1 → RC2) is preferred over reverting a whole milestone, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §2. Because each of Milestones 1–6 is independently revertible on its own, a genuinely serious, hard-to-fix-forward finding can still be isolated to the specific milestone that introduced it and reverted from there without touching earlier, already-verified milestones.

**Estimated complexity:** **M** — verification-heavy rather than code-heavy, but requires the full Docker clean-room pass.

**✅ Milestone 7 complete (2026-07-25) — RC audit, per the project owner's explicit framing: audits things intentionally *not* exercised during implementation, not another round of feature verification.**

**T18 (acceptance walk, fresh):** Re-ran the backend suite (183 passed) and frontend build/lint/tsc fresh at current HEAD rather than trusting Milestone 6's numbers by inheritance — identical results, confirming evidence still matches the actual code. Walked `08_ACCEPTANCE.md` §1–§4 line by line; every criterion now cites a specific test, live action, or code inspection.

**T19 (classify findings):** Zero new findings surfaced by this milestone's own checks. Per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §2: no BLOCKER (no data loss, no security issue, every build/test green, no acceptance criterion provably false). The one real finding of the whole phase — Workbench's dead pinned-tool key — was caught and fixed during Milestone 5, before it ever shipped; not an open item at RC.

**T20a (fresh-checkout reproducibility — added at the project owner's request, 2026-07-25):** Copied the current working tree into a clean directory via `robocopy /XD` excluding `node_modules`/`.venv`/`.venv312`/`.next`/`__pycache__`/`.dev-data*`/`.git` — a filesystem copy rather than a `git worktree`, deliberately, because nothing in this phase has been committed yet and a worktree from HEAD would silently test the *pre-phase* code instead. Backend: brand-new venv, `pip install -r requirements.txt -r requirements-dev.txt`, full suite — 183 passed. Frontend: `npm ci` from `package-lock.json` failed for a **pre-existing, unrelated reason** — this repo's lockfile has Windows-generated optional-dependency entries that don't satisfy any platform's `npm ci`, already documented in `frontend/Dockerfile`'s own comment, confirmed via `git diff` showing zero changes to `package.json`/`package-lock.json` from this phase. Redid the check with `npm install` (the Dockerfile's actual documented command) — clean install, `tsc`/`lint`/`build` all passed from the fresh copy. Cleaned up the copy afterward.

**T20b (Docker Compose clean-room):** Built and ran the full stack in an isolated project (`forge-rc-audit`, port 8587, brand-new named volume) — confirmed via Compose logs that only the five pre-existing migrations (`0001`–`0005`) applied on first boot. Live-verified against the containerized build: setup/unlock, the unified `/converters` page (all ten tools plus Documents), the `/ingest` redirect (`307` via `curl`), and — importantly — the Workbench pinned-tools panel correctly showing "Converter" (proving Milestone 5's fix holds in the actual production image, not just the dev server). Restarted the stack: migration re-run was a no-op, session and pinned-tools state both persisted. Fully torn down (`down -v`) afterward — containers, network, and volume all removed; the user's own environment was never touched.

**T20c (dependency review):** `git diff` on `backend/requirements.txt`, `backend/requirements-dev.txt`, `frontend/package.json`, and `frontend/package-lock.json` against the pre-phase baseline — all four empty. Zero new dependencies anywhere in this phase.

**T20d (repository cleanliness):** `git status --short` shows exactly the files this phase's milestones documented touching — nothing stray. Confirmed `__pycache__`/`.pyc` files present on disk are properly gitignored, not tracked.

**T20e (release notes):** Found the repo's existing per-phase convention (`10_RELEASE_NOTES.md`, templated in `forge-docs/implementation/RELEASE_NOTES_TEMPLATE.md`, precedented by Phase 02). Drafted [`10_RELEASE_NOTES.md`](10_RELEASE_NOTES.md) for this phase — New Features, Breaking Changes (none), Migrations (none), Bug Fixes (the Workbench fix), Known Issues (the pre-existing `.jpg`-without-vision gap and the `npm ci` lockfile drift, both surfaced honestly rather than omitted), Upgrade Notes, and Deferred Work.

**T21 (close-out):** `CURRENT_STATE.md`, `README.md`, and `IMPLEMENT.md` updated to reflect RC-complete status. No stale "in progress" items remain.

**Per the change-type rule (§0.1): Milestone 7 introduced neither an architectural nor a behavioral change**, as expected — this milestone found zero new findings requiring a fix, so its own exception clause (a BLOCKER fix requiring both) was never triggered.

Ready for the project owner's formal Sign-off decision. This is the final milestone — Phase 04's implementation is complete pending that decision.

---

## 1. Task list

- [x] T1 — `test_converters_cron.py` (baseline)
- [x] T2 — `test_ingest_pipeline.py` part A (postprocess/formats/jobs baseline)
- [x] T3 — `test_ingest_pipeline.py` part B (converter/vision baseline)
- [x] T4 — `ConverterProvider` protocol + registry
- [x] T5 — Registry unit tests (fake provider)
- [x] T6 — `MarkItDownProvider` adapter
- [x] T7 — `GET /api/converters/providers` schema + route
- [x] T8 — Provider delegation tests + API contract-preservation tests
- [x] T9 — Frontend `providers.ts` manifest
- [x] T10 — Manifest verification (diff + smoke pass)
- [x] T11 — Unified `/converters` page
- [x] T12 — `/ingest` → `/converters` redirect
- [x] T13 — `nav-registry.ts` consolidation
- [x] T14 — Milestone 5 manual verification pass
- [x] T15 — Full regression sweep
- [x] T16 — Documentation updates
- [x] T17 — Dead-code check
- [x] T18 — RC audit: acceptance criteria walk
- [x] T19 — RC audit: fix + classify findings
- [x] T20a — RC audit: fresh-checkout reproducibility check
- [x] T20b — RC audit: Docker clean-room verification
- [x] T20c — RC audit: dependency review
- [x] T20d — RC audit: repository cleanliness
- [x] T20e — RC audit: release-notes/changelog consistency
- [x] T21 — RC audit: close-out

> Reminder: 10–12 completed tasks is itself a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1. This plan's Milestone 3→4 boundary (T8) lands at 8 tasks; the Milestone 4→5 boundary (T10) lands at 10 — a checkpoint is taken at T10 regardless of exact count, since it's also a milestone boundary and the first with user-visible frontend change ahead of it.

## 2. Task ordering notes

- **Milestone 1** has no dependency on anything and could run in parallel with **Milestone 2** in principle (different files entirely) — sequenced first anyway per the owner's explicit ordering, since its output (baseline tests) is what makes every later milestone's "no regression" claim checkable.
- **Milestone 2** depends on nothing but is sequenced after Milestone 1 for the same reason above, not a code dependency.
- **Milestone 3** requires Milestone 1 (baseline tests to diff against) and Milestone 2 (the protocol/registry it wires into) — a real dependency, not just ordering convention.
- **Milestone 4** has no dependency on Milestones 2–3 (frontend-only) — could run in parallel with them if desired, sequenced here per the owner's list.
- **Milestone 5** requires Milestone 3 (backend endpoint) and Milestone 4 (frontend manifest) — the first milestone that composes prior milestones' outputs into a single user-visible surface.
- **Milestone 6** requires Milestones 1–5 complete — it's an integration check across everything prior, not new work.
- **Milestone 7** requires Milestone 6 complete — the formal audit only makes sense once hardening is done.
- No task in this plan touches Secrets, Notes, Documents, Generators, Crypto, Utilities, Workbench, Search, Project Init, Prompt Studio, or Settings — cross-feature regression risk is limited to the same two additive/consolidating touch points already called out in [`07_TESTING.md`](07_TESTING.md) §4 (`nav-registry.ts`, and the new route addition to `converters.py`'s existing router, not a new router file).

## 3. TODO

- [x] Project-owner review and approval of this milestone breakdown, and of every milestone through Milestone 7. Only remaining item: the project owner's formal Sign-off decision recorded in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §5.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
- [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md)
- [../../14_IMPLEMENTATION_PLAYBOOK.md](../../14_IMPLEMENTATION_PLAYBOOK.md)
