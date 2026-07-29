# ADR-0011 — Model Playground provider credential storage & outbound-call security posture

> **Purpose:** Decide how Model Playground stores user-configured, per-provider LLM API keys, and what security posture governs the outbound calls those keys enable — the "new territory" both [03_ARCHITECTURE.md](../03_ARCHITECTURE.md) §4 and [08_DEFINITION_OF_DONE.md](../08_DEFINITION_OF_DONE.md) §4 flag as unresolved for this phase.
> **Scope:** This decision only. Provider/SDK selection is [ADR-0012](0012-model-playground-provider-sdk-selection.md).
> **Ownership:** Project owner (approved 2026-07-29)
> **Status:** Accepted
> **Version:** 1.0.0
> **Last Updated:** 2026-07-29
> **Depends On:** [../implementation/Phase-05-Model-Playground/01_SPEC.md](../implementation/Phase-05-Model-Playground/01_SPEC.md)
> **Supersedes:** —

---

## 1. Context

Model Playground is the first Forge feature that needs **UI-configurable, per-provider API key storage**. The closest existing precedent, Ingest's optional vision-LLM path (`backend/app/services/ingest/vision.py`), uses a single API key configured once via `FORGE_VISION_API_KEY` (an environment variable, never touched by the UI, never stored in the database). Model Playground's spec requires the opposite: a user adds/removes credentials for multiple providers from the UI, at runtime, without a redeploy.

This is exactly the situation [03_ARCHITECTURE.md](../03_ARCHITECTURE.md) §4 anticipated: *"Does it introduce a provider/API-key concept (Model Playground)? This is new territory for Forge — requires its own security review against `docs/Security.md`."* [08_DEFINITION_OF_DONE.md](../08_DEFINITION_OF_DONE.md) §4 separately flags that no security-review gate exists yet for phases with outbound network calls. Both must be resolved before [`01_SPEC.md`](../implementation/Phase-05-Model-Playground/01_SPEC.md) can be confirmed.

## 2. Decision

1. **Storage mechanism:** Provider credentials live in a new table (proposed name: `ProviderCredential`, final name confirmed in `04_DATABASE.md`) in `backend/app/models/model_playground.py`, with columns for id, `provider` (string/enum), `label`, `encrypted_api_key` (bytes), `created_at`, `updated_at`. The key is encrypted with the **existing** `VaultCrypto` primitive (`app/core/security.py`, `get_vault_crypto()`) — the same `FORGE_MASTER_KEY`-derived SecretBox encryption Secrets already uses. No new crypto library or key-derivation scheme is introduced.
2. **Write-only after creation:** A credential's raw key is accepted on create/update and never returned by any API response afterward — only provider, label, and timestamps are ever read back (mirrors Secrets' pattern of "reveal is an explicit act," except Model Playground doesn't even expose a reveal action — see spec §5, out of scope for v1).
3. **Decrypt only at call time, in-process:** The key is decrypted in `services/model_playground/` immediately before constructing a provider SDK client, held only in local variables for the duration of that call, and never written to logs, error messages, activity records, or the stored run/result rows.
4. **Deleting a credential is independent of run history:** run/result rows store which provider and model were used (plain strings), not a foreign key to the credential and not the key itself — deleting a credential later doesn't corrupt past results (per spec FR4).
5. **Timeouts and failure isolation:** every outbound call gets a hard timeout (proposed default 60s, matching `vision.py`'s existing precedent) and a failure in one provider's call must not raise past the router in a way that fails the whole run — it becomes a per-panel error result (per spec FR7/FR9), consistent with `docs/Security.md`'s existing rule that errors never leak stack traces to the client.
6. **`docs/Security.md` addendum:** add a new "Outbound network calls" section documenting: which features make outbound calls today (Ingest's optional vision-LLM path, Model Playground), what leaves the instance (prompt text and, for Model Playground, whatever the user submits — never `FORGE_MASTER_KEY`, never another provider's key, never Secrets/Vault contents), and that every such feature is opt-in per credential/config (no key configured = feature absent, per [01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md) §1.2). This addendum lands as part of this phase's implementation, not deferred.

## 3. Alternatives considered

- **Store provider keys as regular Secrets records** (reuse `features/vault`/`services/secrets` directly): rejected. It would either require Model Playground's service layer to import `services/secrets` internals — a cross-feature import forbidden by [07_CODING_STANDARDS.md](../07_CODING_STANDARDS.md) §1 — or require Secrets to grow provider-specific concepts it has no other reason to know about. The two also have genuinely different lifecycles: a Secret is revealed by explicit human action and logged every time; a provider credential is auto-decrypted at call time with no per-call reveal-and-log step (that would be excessive for something invoked on every prompt run). Conflating them would blur both.
- **Keep keys in `.env` only, like `vision.py`:** rejected outright — the spec's explicit requirement is UI-configurable, multi-provider keys without a redeploy. An env-var-only design cannot satisfy FR1/FR4.
- **A dedicated secrets-manager abstraction shared by both Secrets and Model Playground:** considered as a "do it right once" option, but rejected for v1 as premature generalization — there is exactly one other consumer (Secrets) and it isn't asking for this; per [01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)'s general bias against building for hypothetical future needs, a second concrete need should exist before generalizing (same reasoning ADR-0008 already applied to the Capability Registry).

## 4. Consequences

- **Easier:** any future phase needing an outbound-provider credential (none currently on the roadmap beyond this) has a template to follow — dedicated table + `core/security.py` crypto, never another feature's internals.
- **Harder / forecloses:** credential rotation for this feature is UI+DB only, not `.env` — an operator who prefers env-var-managed secrets for this specific use case doesn't get that option in v1.
- **Touches:** [03_ARCHITECTURE.md](../03_ARCHITECTURE.md) §2 invariant "features never import from each other's internals" (this decision is what keeps Model Playground compliant with it) and [`docs/Security.md`](../../docs/Security.md) (gets a new section, per §2.6 above).
- **Resolves** the [03_ARCHITECTURE.md](../03_ARCHITECTURE.md) §4 and [08_DEFINITION_OF_DONE.md](../08_DEFINITION_OF_DONE.md) §4 open TODOs for this phase specifically; both documents should have their TODO markers updated to point here once this ADR is Accepted.

## 5. Cross-references

- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [../08_DEFINITION_OF_DONE.md](../08_DEFINITION_OF_DONE.md)
- [../implementation/Phase-05-Model-Playground/01_SPEC.md](../implementation/Phase-05-Model-Playground/01_SPEC.md)
- [0012-model-playground-provider-sdk-selection.md](0012-model-playground-provider-sdk-selection.md)
- [../../docs/Security.md](../../docs/Security.md)
