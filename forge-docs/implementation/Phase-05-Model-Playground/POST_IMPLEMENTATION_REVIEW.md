# Model Playground — Post-Implementation Review

> **Purpose:** A retrospective on how Phase 05 actually went — not a restatement of what was built (see `CURRENT_STATE.md`/`08_ACCEPTANCE.md` for that), but what the process revealed.
> **Scope:** This phase's full arc: specification, the two blocking ADRs, T1–T19 implementation, and the RC audit.
> **Status:** Final — Phase 05 at Release Candidate, owner sign-off recorded, pending PR merge.
> **Last Updated:** 2026-07-29
> **Depends On:** [CURRENT_STATE.md](CURRENT_STATE.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md), [QA/README.md](QA/README.md)

---

## What Went Well

- **Stopping for the two blocking ADRs before writing any code paid off exactly as designed.** `03_ARCHITECTURE.md` §4 and `08_DEFINITION_OF_DONE.md` §4 had flagged, since Phase 05 was scaffolded, that provider credential storage and outbound-call security posture were unresolved. Drafting [ADR-0010](../../decisions/0010-model-playground-provider-credential-security.md)/[ADR-0011](../../decisions/0011-model-playground-provider-sdk-selection.md) as concrete proposals (not vague questions) and getting a real yes/no/adjust decision in one round-trip meant implementation never had to guess at the credential-storage design or provider list.
- **Reusing `get_vault_crypto()` instead of inventing a new encryption scheme kept this phase's biggest risk (a new credential-storage concept) small.** Secrets already proved the encryption-at-rest pattern; Model Playground applies the same primitive to a new table rather than adding a second crypto approach to the codebase.
- **The provider-adapter interface (`ProviderAdapter` protocol) made "two providers, one orchestration path" clean.** `runs.py`'s dispatch logic never branches on provider identity — it just calls `spec.adapter.complete(...)` — so the failure-isolation and timeout logic is provider-agnostic and was easy to test with a fake adapter instead of mocking two different SDKs' internals.
- **Manual verification used the real OpenAI API, not a mock, for the browser pass.** Configuring a real (invalid) key and watching the actual 401 flow through to a clean "Authentication failed" message end-to-end caught the one thing that matters most for this phase's security posture — that a real provider error never leaks a stack trace or raw exception text to the client — in a way a mocked test alone wouldn't have proven.
- **The plain-string (not foreign-key) design for `PlaygroundResult.provider`/`.model` (ADR-0010 §2.4) was tested, not just designed.** `test_deleting_credential_does_not_corrupt_past_run_results` exercises exactly the scenario the design exists to protect against, and it passes.

## What Didn't

- **The RC audit found zero BLOCKER/MAJOR/MINOR issues** — a genuinely clean pass, not a gap to report. The one open item (keyboard-activation verification) is an *unverified claim* per [`../../12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4, not a bug — see QA-0001.
- **08_ACCEPTANCE.md's UX criteria weren't flagged upfront as needing a human/device session**, the same gap Phase 01's review already recommended fixing ("Identify which acceptance criteria structurally require a human/device session up front, at spec time"). This phase repeated that miss for AC18 specifically — it wasn't obvious until the manual verification pass actually hit the tool's Enter-key limitation.

## Unexpected Problems

- **The automated browser tool's synthetic Enter/Space keypresses did not activate a focused native `<button>`**, even though the identical element responded instantly to a mouse click. This was investigated properly rather than assumed: the same non-activation was reproduced on the pre-existing Secrets page's "New secret" button (a control this phase never touched), and cross-referencing [Phase 01's `POST_IMPLEMENTATION_REVIEW.md`](../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md) found the exact same root cause already documented there a month earlier ("dispatched Enter/Space key presses arrived with an empty `key` field"). Confirming a "looks like our bug" symptom is actually a known, pre-existing tool artifact — before writing it up as a finding — is what kept this from becoming a false BLOCKER.
- **`get_page_text` doesn't see portaled dialog content.** Early in verification, a `Dialog`/`AlertDialog` appearing to "not open" after a click was actually the tool reading only `<main>`'s text while the dialog rendered into a portal outside it. Switching to `read_page` (full accessibility tree) resolved the false alarm. Worth naming so a future session doesn't repeat the same few minutes of confusion.
- **Two separate throwaway dev-data directories were used** (`backend/.dev-data-verify/`, cleaned up after each verification pass) via the repo's existing `backend-verify`/`frontend-verify` launch configs — no new environment setup was needed since Phase 01–04 already established this pattern.

## Architecture Changes

None beyond what the accepted ADRs called for. Specifically confirmed:

- No new crypto primitive — `VaultCrypto`/`get_vault_crypto()` reused exactly as ADR-0010 specified.
- No third provider, no "Custom/OpenAI-compatible" pseudo-provider — ADR-0011 §2.3's deferral held; only `openai`/`anthropic` appear in `PROVIDER_REGISTRY`.
- No cross-feature import — `services/model_playground/` never imports `services/secrets/*`; the only shared dependency is `app/core/security.py`, a `core/` module per `03_ARCHITECTURE.md` §2's own carve-out.
- One deliberate, spec-consistent addition beyond the original ADRs' text: registering `"model_playground"` in `services/workbench.py`'s `WORKBENCH_TOOL_KEYS`, matching every prior phase's precedent (Secrets, Notes, Documents, ..., Prompt Studio all did the same) so the new page can be pinned to the Workbench. This wasn't explicitly named in `03_BACKEND.md`'s integration section, but it's the established pattern for every other feature page in the app, not a new one invented for this phase.

## Performance Notes

- Each outbound provider call has a 60-second hard timeout (`TIMEOUT_SECONDS` in `runs.py`), matching the existing vision-LLM precedent in `services/ingest/vision.py`. Calls dispatch concurrently (`asyncio.gather`), so a run's total wall-clock time is bounded by its slowest single target, not the sum of all targets — verified functionally (`test_create_run_timeout_is_isolated_to_that_target`), not independently benchmarked under load. No load/concurrency-at-scale testing was performed; this is a single-tenant, single-operator feature per Forge's own threat model, so it wasn't treated as in-scope for this phase.
- No new hot-path computation was added to any existing endpoint — Model Playground's tables and routes are entirely additive; nothing on an existing request path got slower.

## Accessibility Notes

- Tab order was verified correct across the full page (provider actions → prompt composer → checkboxes → submit → history rows) via the accessibility tree, both at desktop and mobile (375×812) viewports, in both light and dark mode.
- Delete confirmations (credential removal, run deletion) both use the existing `AlertDialog` primitive and were verified to require an explicit click before anything is removed — no silent deletes.
- Not verified: real-hardware keyboard-only activation (Enter/Space on a focused button) — see QA-0001. This is the one QA item carried out of this phase, tracked openly rather than silently assumed passing.

## Lessons Learned

1. **A concrete, drafted decision gets approved faster than an open question.** Presenting ADR-0010/ADR-0011 as fully-reasoned proposals (with alternatives considered and consequences stated) rather than "what should we do about credentials?" turned a potentially multi-round negotiation into a single approve-with-one-adjustment round-trip.
2. **When a verification tool produces a surprising result, check whether it's already been seen before you write it up as new.** This phase's keyboard-activation "bug" turned out to be independently documented in a different phase's retrospective a month earlier. A five-minute grep through `history/` turned a would-be new finding into a two-line confirmation.
3. **"Verified live" and "verified by an automated test" are different claims worth keeping distinct in the acceptance-criteria writeup**, per Phase 01's own recommendation — this phase's `08_ACCEPTANCE.md` names, for almost every criterion, which specific test or live action verified it, which is what made this review possible to write without re-deriving anything.
4. **Reuse-first ("does an existing pattern already solve this?") is worth deliberately checking before designing new backend/frontend structure**, not just for crypto (`get_vault_crypto()`) but for smaller things too — the Workbench pinned-tools registration would have been easy to miss if the existing `services/workbench.py` file hadn't been read before considering the backend implementation "done."

## Recommendations for Phase 06

- **Name, in `08_ACCEPTANCE.md` itself, which criteria structurally need a real device/human session** (per Phase 01's own recommendation, repeated here because it was missed again) — do this at spec time, not discovered during the RC pass.
- **When an automated verification session produces an unexpected result, check `history/*/POST_IMPLEMENTATION_REVIEW.md` for a prior phase hitting the same tool limitation before concluding it's a new app bug.** This phase's keyboard-activation finding is now the second independent confirmation of the same tool artifact — a third occurrence should probably get promoted from a per-phase QA ticket to a standing, cross-phase note (maybe in `14_IMPLEMENTATION_PLAYBOOK.md` §12) so future phases don't have to re-discover and re-verify it each time.
- **Check whether a new feature needs registration in Workbench's `WORKBENCH_TOOL_KEYS`/pinned-tools list early**, not as an afterthought — every phase since Phase 01 has needed this, so it's effectively a standing integration point, not an optional one.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [QA/README.md](QA/README.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md](../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md)
