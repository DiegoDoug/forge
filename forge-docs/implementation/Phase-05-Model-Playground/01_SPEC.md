# Model Playground — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Confirmed — [ADR-0011](../../decisions/0011-model-playground-provider-credential-security.md) and [ADR-0012](../../decisions/0012-model-playground-provider-sdk-selection.md) both Accepted 2026-07-29.
> **Last Updated:** 2026-07-29

---


## 1. Summary

Model Playground is a UI for sending the same prompt to one or more configured LLM provider/model combinations and comparing their outputs side by side. Each provider is enabled by configuring an API key for it; a provider with no key configured simply doesn't appear as a runnable option (per [01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md) §1.2 — graceful degradation, not a broken app).

This is the first Forge feature whose core purpose is first-class outbound calls to third-party LLM providers, and the first to need **UI-configurable, per-provider API key storage** (distinct from Ingest's single env-var-configured optional vision-LLM key). Both of those are new territory for Forge — see §6 Open questions and the two linked ADRs, which must be resolved before implementation begins.

## 2. User stories

- As a user, I want to configure an API key for a supported LLM provider, so that I can run prompts against that provider's models without editing environment variables or redeploying.
- As a user, I want to see, at a glance, which providers are currently usable (key configured) and which are not, so that I understand why a provider isn't in my comparison options.
- As a user, I want to write one prompt and send it to multiple provider/model combinations at once, so that I can compare their responses side by side without repeating myself.
- As a user, I want each provider/model's response to load and fail independently, so that one slow or erroring provider doesn't block or blank out the others.
- As a user, I want to see basic run metadata (model name, latency, token usage if the provider reports it, error message if it failed) alongside each response, so that I can judge cost/quality tradeoffs, not just read raw text.
- As a user, I want to revisit my recent prompt runs, so that I don't lose a useful comparison the moment I navigate away.
- As a user, I want to delete a stored provider API key, so that I can revoke access without deleting my run history.
- As a user, I want the master password / session gate to protect my provider keys the same way it protects Secrets, so that stolen `forge.db` contents are as useless here as everywhere else in Forge.

## 3. Functional requirements

**Provider credentials**
- FR1: The user can add a credential for a supported provider (see ADR-0012 for the v1 provider list) consisting of, at minimum, a label and an API key.
- FR2: Credential values are encrypted at rest using the existing `VaultCrypto` primitive (`app/core/security.py`, `get_vault_crypto()`) — the same encryption-at-rest guarantee Secrets already provides — not a new crypto scheme (see ADR-0011).
- FR3: A stored credential's key value is never returned to the client after creation — the UI can only show that a credential exists (label, provider, created/updated timestamps), matching Secrets' "reveal is an explicit, logged action" pattern. Revealing the raw key is out of scope for v1 (see §5) — a credential can be replaced or deleted, not viewed.
- FR4: The user can delete a provider credential. Deleting a credential does not delete past run history that used it (past responses remain readable; the run row records which provider/model was used, not the credential's live key).
- FR5: A provider with no credential configured does not appear in the runnable provider/model list. This must be true with zero configuration and zero internet access (per [01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md) §1.2) — the rest of Forge works normally.

**Prompt comparison run**
- FR6: The user can write a single prompt (plain text; multi-turn chat history is out of scope for v1, see §5) and select one or more provider/model combinations to send it to.
- FR7: Each selected provider/model call executes independently — one provider failing or timing out does not block or fail the others' results.
- FR8: Each result panel shows: the response text, the model identifier, wall-clock latency, token usage if the provider's API reports it, and, on failure, a user-legible error message (never a raw stack trace — per [`../../../docs/Security.md`](../../../docs/Security.md) "Input handling").
- FR9: Every outbound call has a hard timeout (proposed default: 60s, matching the existing vision-LLM precedent in `services/ingest/vision.py`) after which that panel shows a timeout error; it does not hang the UI.
- FR10: A completed run (prompt + all panel results) is persisted so the user can return to it later (see §4/ADR-0011 for what is and isn't stored).

**History**
- FR11: The user can see a list of their past runs (prompt text, providers/models used, timestamp) and reopen one to view its stored results.
- FR12: The user can delete a past run.

## 4. Relationship to existing features

New capability — the first Forge feature with first-class outbound LLM provider calls as its core purpose (Ingest's vision-LLM path is optional/secondary by comparison, and its key is env-var-only, not user-configurable from the UI).

Reuses, rather than reinvents:
- `app/core/security.py`'s `VaultCrypto`/`get_vault_crypto()` for credential encryption at rest (same primitive Secrets uses, applied to a new table — not a new cross-feature import, since it lives in `core/`).
- The existing app shell, auth session, and command palette (per [01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md) §1.7) — Model Playground is a normal `app/(app)/` page, not a parallel auth or navigation system.
- The `services/<feature>/` + thin-router pattern from [03_ARCHITECTURE.md](../../03_ARCHITECTURE.md) §1.1 — new `services/model_playground/` subpackage, no edits to `services/secrets/` or `services/ingest/`.

Does not reuse:
- The Secrets feature's storage directly. See ADR-0011 §3 for why provider credentials get their own table rather than being stored as regular Secret rows.

## 5. Explicitly out of scope (v1)

- Multi-turn chat / conversation history within a single run — v1 is single-prompt, single-turn per provider/model.
- Streaming responses (SSE/token-by-token rendering) — v1 waits for each provider's complete response. Revisit once non-streaming is proven stable; streaming adds meaningful complexity (partial-failure UI states, cancellation) not justified for a first cut.
- Revealing a stored credential's raw key value after creation (write-only, like a password field — replace or delete only).
- Cost estimation / billing tracking beyond echoing whatever token-usage numbers a provider's API returns.
- Any provider not explicitly approved in ADR-0012.
- Sharing a run with another user (Forge is single-tenant — no concept of "another user" applies here anyway, per [01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md) §1.1).
- Prompt template management / versioning — that's Prompt Studio's (Phase 03) territory; Model Playground consumes a raw prompt string the user types or pastes, it does not manage a prompt library. (Sequencing note from [02_ROADMAP.md](../../02_ROADMAP.md) §4: Phase 03 was resolved to have zero shared plumbing with Phase 05 — nothing here changes that; Model Playground does not read from or write to Prompt Studio's storage.)

## 6. Open questions

The two blocking questions are resolved:

- [x] **Resolved by [ADR-0011](../../decisions/0011-model-playground-provider-credential-security.md)** (Accepted 2026-07-29): provider API keys live in a new `ProviderCredential` table, encrypted with the existing `VaultCrypto` primitive, write-only after creation, decrypted only in-memory at call time. `docs/Security.md` now has an "Outbound network calls" section.
- [x] **Resolved by [ADR-0012](../../decisions/0012-model-playground-provider-sdk-selection.md)** (Accepted 2026-07-29): v1 ships OpenAI + Anthropic via their official SDKs behind a per-provider adapter interface. A generic "Custom / OpenAI-compatible" pseudo-provider is explicitly deferred, not in v1.

Remaining, non-blocking (resolved in the docs named):

- [x] Resolved in `02_UI.md`: an unconfigured provider appears in the credential/provider list greyed out with a "configure a key" call to action, rather than being invisible — this keeps the two supported providers discoverable even before a key is added.
- [x] Resolved in `04_DATABASE.md`: run history is retained indefinitely (like Secrets/Notes), manual delete only — no TTL/cap. A run is user-authored comparison data, not scratch conversion output.

## 7. TODO

- [ ] Assign a phase owner.

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [04_DATABASE.md](04_DATABASE.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
- [../../decisions/0011-model-playground-provider-credential-security.md](../../decisions/0011-model-playground-provider-credential-security.md)
- [../../decisions/0012-model-playground-provider-sdk-selection.md](../../decisions/0012-model-playground-provider-sdk-selection.md)
