# ADR-0013 — Model Playground: DeepSeek, additional named providers, and a generic OpenAI-compatible provider

> **Decision summary (approved 2026-08-02):** Extends [ADR-0012](0012-model-playground-provider-sdk-selection.md)'s "exactly OpenAI + Anthropic, nothing more without a new ADR" constraint. Adds DeepSeek, Kimi (Moonshot), GLM (Zhipu), and Gemini as named providers, plus a user-configurable "Custom (OpenAI-compatible)" pseudo-provider with a `base_url` field — the exact extension ADR-0012 §2.3/§4 anticipated and explicitly deferred.

> **Purpose:** Let users choose their AI provider and use their own credentials, without hard-coding Forge around a single vendor, while keeping the change additive to the adapter boundary ADR-0012 established.
> **Scope:** Provider/SDK selection and the credential schema shape needed to support a user-supplied endpoint. Credential storage/security posture remains governed by [ADR-0011](0011-model-playground-provider-credential-security.md) — this ADR does not change that decision, it extends the schema it defined with one new optional field.
> **Ownership:** Project owner (approved 2026-08-02)
> **Status:** Accepted
> **Version:** 1.0.0
> **Last Updated:** 2026-08-02
> **Depends On:** [0011](0011-model-playground-provider-credential-security.md), [0012](0012-model-playground-provider-sdk-selection.md)
> **Supersedes:** —

---

## 1. Context

Phase 05 (Model Playground) shipped and froze with exactly two providers (OpenAI, Anthropic), per ADR-0012, which explicitly designed the adapter boundary in `services/model_playground/providers/` so that "adding a third provider later is additive (a new adapter file), not a rewrite," and explicitly deferred a "Custom / OpenAI-compatible" pseudo-provider to a future phase.

That future need has arrived: users want to point Model Playground at DeepSeek, Moonshot (Kimi), Zhipu (GLM), and arbitrary self-hosted or third-party OpenAI-compatible endpoints (mirroring the precedent already established by Ingest's `vision.py`, which calls `openai.AsyncOpenAI`/`OpenAI` generically against any `base_url`). This is a small, additive infrastructure enhancement, not a reopening of Phase 05's frozen specification — no existing endpoint, schema field, or UI flow for OpenAI/Anthropic changes behavior.

## 2. Decision

1. **No new SDK dependency.** DeepSeek, Kimi, GLM, and Gemini all expose (or Google additionally exposes, via its `/v1beta/openai/` compatibility layer) an OpenAI-compatible `chat.completions` surface. All of them, plus the generic "Custom" provider, are served by one new adapter class, `OpenAICompatibleAdapter` (`services/model_playground/providers/openai_compatible_adapter.py`), constructed with a `base_url`. No `if provider == "deepseek"` branching exists anywhere outside the registry construction — the registry is the only place a provider key maps to adapter behavior, consistent with ADR-0012 §2.2's boundary.
2. **Named providers get a fixed `base_url` baked into their registry entry:**
   - `deepseek` → `https://api.deepseek.com/v1`
   - `kimi` → `https://api.moonshot.cn/v1`
   - `glm` → `https://open.bigmodel.cn/api/paas/v4`
   - `gemini` → `https://generativelanguage.googleapis.com/v1beta/openai/` (Google's OpenAI-compatibility layer — "where practical" per the request; if this ever proves materially incompatible in practice, Gemini gets its own adapter later, per ADR-0012's original escape hatch, without touching any other provider).
   Each keeps a small curated `models` tuple, exactly like OpenAI/Anthropic today — no model-discovery call is added, since the existing UI/validation pattern (checkboxes rendered from `provider.models`, `RunTargetIn` validated against that tuple) already works for a short curated list and adding live model discovery is not required by any current acceptance criterion.
3. **New "Custom (OpenAI-compatible)" pseudo-provider (`custom`):** the one case that genuinely needs new schema surface. Its `base_url` is user-supplied at credential-configuration time (not fixed in the registry), and its model is free text at run-submission time (empty `models` tuple, `allows_custom_model=True` on `ProviderSpec`) rather than a fixed checkbox list, since Forge cannot know a self-hosted or third-party-compatible deployment's model catalogue ahead of time.
4. **`ProviderCredential` gains one new nullable column, `base_url`.** Only used (required) when `PROVIDER_REGISTRY[provider].requires_base_url` is true (currently only `custom`); rejected as an unexpected field for every fixed-endpoint provider, so a user can't accidentally point a named provider's key at a different host by supplying a stray `base_url`. This is exactly the schema change ADR-0012 §4 flagged as the one consequence of accepting the deferred Custom provider. `base_url` is not treated as a secret (ADR-0011's write-only/never-returned rule stays scoped to `api_key`); it is safe to echo back in `ProviderCredentialOut` so the UI can show what endpoint is configured.
5. **`ProviderAdapter` protocol gains one new optional keyword, `base_url: str | None = None`.** The OpenAI and Anthropic adapters accept and ignore it (each already owns a fixed client-construction path that needs no base URL override) — this keeps `runs.py`'s call site (`spec.adapter.complete(api_key=..., model=..., prompt=..., base_url=...)`) uniform across every provider, so orchestration code never branches on which provider it's calling.
6. **A new stateless connection-test endpoint** (`POST /model-playground/providers/test-connection`) lets a user validate provider/credential/base_url/model *before* saving anything — it accepts the same shape as a credential-create request, makes one real minimal completion call through the same adapter path, and returns success/failure without writing to the database. This did not exist for OpenAI/Anthropic in v1 either; it's a genuinely new capability, added here because the brief requires it and because a user-supplied `base_url` is exactly the kind of input that benefits from a pre-save check (a typo'd endpoint currently only surfaces as an opaque per-run error).
7. **SSRF review of `base_url`:** see §4 below — no network-level allowlist is added; this is deliberate and documented, not an oversight.

## 3. Alternatives considered

- **A generic "provider config" table keyed by an arbitrary user-chosen name (supporting multiple simultaneous custom endpoints):** rejected for this pass. `ProviderCredential` already has a hard uniqueness constraint of one row per `provider` string (ADR-0011 §2.1); generalizing that to let users register N custom endpoints would touch the run-target/model-selection UI more invasively (provider becomes dynamic, not a fixed registry key) for a need not established by the brief (which asks for "a" custom endpoint, singular, to be configurable). If real multi-custom-endpoint demand shows up, it is additive from here: promote `custom` from a single fixed key to a small user-managed list, without touching the OpenAI/Anthropic/DeepSeek/Kimi/GLM/Gemini path at all.
- **A third-party abstraction library (LiteLLM, etc.) instead of one more internal adapter:** rejected for the same reason ADR-0012 §3 rejected it originally — the marginal cost of one more thin adapter class is lower than adopting a new dependency's own compatibility surface, especially now that the adapter is generic enough to cover five provider keys with zero per-vendor code.
- **Live model discovery (a `/models` call) instead of curated lists for the new named providers:** rejected as unnecessary scope for this change — the existing curated-list pattern already satisfies "the system must always know which model is being requested" (§9 of the brief) and adding discovery is real, untested surface (rate limits, differing response shapes per vendor) for a "nice to have," not a stated requirement.
- **Blocking private/loopback addresses in `base_url` as a hard SSRF mitigation:** rejected — see §4.

## 4. SSRF assessment for user-supplied `base_url`

Forge's threat model ([`docs/Security.md`](../../docs/Security.md) "Threat model") is explicit: a single trusted operator per instance, no multi-tenancy, and the model does not defend against a malicious operator (who already has the master key and an unlocked session in-process). The `custom` provider's `base_url` is configurable only by that same single authenticated operator, through the same session-gated API every other Model Playground credential goes through (`AuthDep`) — there is no second, lower-trust user who could point the *operator's own* server at an internal address on the operator's behalf. This is qualitatively different from a multi-tenant SaaS SSRF, where a low-trust user could pivot the *service's* privileged network position to reach infrastructure the user has no other route to.

Forge also already has a live precedent for exactly this input shape: `FORGE_VISION_BASE_URL` (`app/services/ingest/vision.py`) is operator-controlled, unrestricted, and explicitly documented in `docs/Security.md` as pointing at "OpenAI by default, or any OpenAI-compatible endpoint" — including self-hosted ones on the operator's own LAN, which is a legitimate, intended use case ADR-0012 §3 itself named ("self-hosted models, OpenRouter, etc."). Blocking loopback/private-range addresses for `custom`'s `base_url` would break that exact legitimate use case (pointing at a local Ollama/vLLM/LM Studio instance) while adding no protection against the actual party who controls the value.

Given that, the decision is: validate `base_url` is a well-formed `http(s)://` URL (reject empty, non-HTTP(S) schemes such as `file://`, and enforce a sane max length) at the Pydantic schema layer, and go no further. No network-level allowlist, no DNS-rebinding protection, no cloud-metadata-address blocklist is added, because none of those defend against the actual threat actor this feature is exposed to (the trusted operator themselves) and all of them would foreclose the feature's stated purpose. If Forge's threat model ever changes (e.g. a multi-tenant mode is added), this decision must be revisited — flagged here explicitly so it isn't silently inherited into a context where it no longer holds.

## 5. Consequences

- **Easier:** a sixth, seventh, ... named OpenAI-compatible-shaped provider is a two-line registry addition, per ADR-0012's original design goal — this ADR is the proof that goal held.
- **Harder / forecloses:** exactly one custom endpoint can be configured at a time (see §3); a provider whose API is *not* OpenAI-compatible in shape (e.g. a hypothetical future provider with a fundamentally different request/response contract) still needs its own adapter file, same as Anthropic did.
- **Touches:** [06_TECH_STACK.md](../06_TECH_STACK.md) (no new dependency row — worth noting explicitly since that's unusual), [`docs/Security.md`](../../docs/Security.md) (outbound-network-calls section gets the new providers + the SSRF assessment in §4 above), [ADR-0011](0011-model-playground-provider-credential-security.md)'s schema (one new nullable, non-secret column).

## 6. Cross-references

- [0011-model-playground-provider-credential-security.md](0011-model-playground-provider-credential-security.md)
- [0012-model-playground-provider-sdk-selection.md](0012-model-playground-provider-sdk-selection.md)
- [../06_TECH_STACK.md](../06_TECH_STACK.md)
- [../../docs/Security.md](../../docs/Security.md)
- [../implementation/Phase-05-Model-Playground/01_SPEC.md](../implementation/Phase-05-Model-Playground/01_SPEC.md)
