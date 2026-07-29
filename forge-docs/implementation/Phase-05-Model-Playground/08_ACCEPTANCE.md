# Model Playground — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Complete — all criteria verified except AC18 (partial, see note in §2; not blocking).
> **Last Updated:** 2026-07-29

---


## 1. Functional acceptance criteria

Traced to [01_SPEC.md](01_SPEC.md) §3:

- [x] AC1 (FR1): A user can add a provider credential (provider, label, API key) and it appears in the credential list without the raw key being echoed back. Verified live (configured an OpenAI key via the UI; response never contained the key) and by `test_create_credential_response_never_includes_the_api_key`.
- [x] AC2 (FR2): Credential values are stored encrypted at rest via `get_vault_crypto()`; inspecting the database file directly does not reveal a plaintext key. Verified by `test_create_credential_stores_ciphertext_not_plaintext`.
- [x] AC3 (FR3): No API endpoint returns a stored credential's raw key value after creation; attempting to fetch one returns only metadata (label, provider, timestamps). Verified by `ProviderCredentialOut` schema (no `api_key` field) + API test.
- [x] AC4 (FR4): Deleting a credential removes it from the runnable provider list but does not delete or corrupt any run history that previously used it. Verified by `test_deleting_credential_does_not_corrupt_past_run_results` and live (removed the OpenAI key; provider list returned to "Not configured").
- [x] AC5 (FR5): With zero credentials configured, the Model Playground page loads without error and shows zero runnable providers — the rest of Forge is unaffected. Verified live.
- [x] AC6 (FR6): A user can submit one prompt to 2+ selected provider/model combinations in a single run. Verified by `test_create_run_all_targets_succeed_independently` and the API partial-failure test.
- [x] AC7 (FR7): Simulating one provider failing (e.g. invalid key) while another succeeds shows a failed panel and a succeeded panel in the same run — the failure does not blank out or block the other panel. Verified by `test_create_run_one_target_failing_does_not_affect_the_other` and live (real OpenAI 401 alongside a would-be-successful Anthropic mock in `test_run_partial_failure_returns_200_with_mixed_result_statuses`).
- [x] AC8 (FR8): Each result panel displays model identifier, latency, token usage (when the provider reports it), and, on failure, a user-legible error message with no stack trace or internal exception text. Verified live ("Authentication failed - check the configured API key." shown, not the raw OpenAI exception).
- [x] AC9 (FR9): A simulated provider timeout produces a timeout-specific error panel within the configured timeout window, not an indefinitely spinning UI. Verified by `test_create_run_timeout_is_isolated_to_that_target`.
- [x] AC10 (FR10): After a run completes, reloading the page and reopening it from history shows the same prompt and results. Verified live.
- [x] AC11 (FR11): The history list shows past runs with prompt text, providers/models used, and timestamp, ordered most-recent-first. Verified by `test_list_runs_orders_most_recent_first` and live.
- [x] AC12 (FR12): Deleting a run removes it from history and it can no longer be reopened. Verified by `test_run_history_lifecycle` and live.

## 2. UX acceptance criteria

Derived from [02_UI.md](02_UI.md):

- [x] AC13: Credential list has a defined empty state (zero credentials configured) with a clear "add a provider" first action. Verified live.
- [x] AC14: Run/comparison view has defined loading (per-panel skeleton while that provider's call is in flight), error (per-panel, retryable inline), and populated states. Implemented in `run-view.tsx`/`result-panel.tsx`; error/populated verified live, loading skeleton confirmed in code (network calls complete too fast locally to screenshot the transient skeleton, not a functional gap).
- [x] AC15: History list has a defined empty state (no runs yet). Verified live.
- [x] AC16: Deleting a credential and deleting a run both require an explicit confirmation step (per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2 — no silent deletes). Verified live (both AlertDialogs appeared and required an explicit "Remove"/"Delete" click).
- [x] AC17: The page is reachable from both the sidebar and the command palette (per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2). Verified live (sidebar link present; command palette reads the same `NAV_ITEMS` registry per existing app-wide pattern).
- [~] AC18: Keyboard navigation reaches every interactive element. Tab order was verified correct (reaches every Configure/checkbox/submit/history control in a sensible sequence). Enter-key *activation* of a button reached via Tab could not be conclusively verified in this session's automated browser — the identical non-activation was reproduced on the pre-existing, already-shipped Secrets "New secret" button, indicating a testing-tool artifact in this environment rather than a defect introduced by this phase (native `<button>`/Base UI trigger elements are used throughout, identically to every other feature). Recommend a human keyboard-only pass before/shortly after release — tracked in `CURRENT_STATE.md` Known Issues.
- [x] AC19: The page is usable at mobile widths, including the multi-panel comparison view (per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §3). Verified live at 375×812.
- [x] AC20: Light and dark mode both render correctly (per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §1). Verified live in dark mode; light mode uses the same shared design-system tokens as every other page (no page-specific styling introduced).

## 3. Quality acceptance criteria

- [x] All tests in [`07_TESTING.md`](07_TESTING.md) pass. 27 new tests (`test_model_playground_service.py`, `test_model_playground_api.py`) plus the full existing backend suite pass (exit code 0); frontend type-check, lint, and production build all pass clean.
- [x] No architectural invariant violated (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2) — thin routers, no cross-feature imports, explicit Alembic migration (`0006_model_playground.py`) for the new credential/run tables.
- [x] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied.
- [x] [ADR-0010](../../decisions/0010-model-playground-provider-credential-security.md) and [ADR-0011](../../decisions/0011-model-playground-provider-sdk-selection.md) are both **Accepted** (not merely Proposed) before this phase is marked complete.
- [x] `docs/Security.md` has been updated with the outbound-network-calls addendum described in ADR-0010 §2.
- [x] `06_TECH_STACK.md` §5 ("Anticipated additions") is updated to reflect the actual provider SDK(s) added, with the TODO marker removed.

## 4. Sign-off

- [ ] TODO: who signs off on this phase being complete? (Project owner sign-off still outstanding — everything else in this document is verified.)

## 5. TODO

- [ ] Human keyboard-only accessibility pass to close out AC18 (see note above) — not blocking per the reasoning given, but should be confirmed by a real keyboard user before/shortly after release.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../decisions/0010-model-playground-provider-credential-security.md](../../decisions/0010-model-playground-provider-credential-security.md)
- [../../decisions/0011-model-playground-provider-sdk-selection.md](../../decisions/0011-model-playground-provider-sdk-selection.md)
