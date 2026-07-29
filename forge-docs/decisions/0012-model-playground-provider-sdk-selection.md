# ADR-0012 — Model Playground provider & SDK selection (v1)

> **Decision summary (approved 2026-07-29):** v1 ships OpenAI + Anthropic via their official SDKs behind a per-provider adapter interface. A "Custom / OpenAI-compatible" pseudo-provider is explicitly **deferred**, not included in v1 — see §2.3.

> **Purpose:** Decide which LLM provider(s) Model Playground supports at launch and which SDK dependency each requires — the choice [06_TECH_STACK.md](../06_TECH_STACK.md) §5 has flagged as "not yet chosen" since Phase 05 was scaffolded.
> **Scope:** This decision only. Credential storage/security posture is [ADR-0011](0011-model-playground-provider-credential-security.md).
> **Ownership:** Project owner (approved 2026-07-29)
> **Status:** Accepted
> **Version:** 1.0.0
> **Last Updated:** 2026-07-29
> **Depends On:** [../implementation/Phase-05-Model-Playground/01_SPEC.md](../implementation/Phase-05-Model-Playground/01_SPEC.md)
> **Supersedes:** —

---

## 1. Context

Model Playground's stated mission is to "test/compare LLM providers and models side by side" — the value proposition depends on supporting more than one provider. [06_TECH_STACK.md](../06_TECH_STACK.md) §5 lists this as an anticipated-but-undecided dependency addition, and [decisions/README.md](README.md) §1 requires an ADR whenever a new external dependency *category* is introduced. Forge already depends on the `openai` PyPI package (used by `services/ingest/vision.py`, called generically against any OpenAI-compatible `base_url` — including self-hosted or third-party-compatible endpoints, not necessarily OpenAI's own servers).

## 2. Decision

1. **v1 ships two named providers:**
   - **OpenAI** — reuses the `openai` PyPI dependency already in `backend/requirements.txt`. No new dependency.
   - **Anthropic** — new dependency: the `anthropic` PyPI package.
2. **Adapter boundary:** each provider is implemented behind a small internal interface in `services/model_playground/providers/` (e.g. `openai.py`, `anthropic.py`), so adding a third provider later is additive (a new adapter file), not a rewrite of the run-orchestration logic.
3. **"Custom / OpenAI-compatible" pseudo-provider: deferred, not in v1.** Considered — it would let a user point at any OpenAI-compatible `base_url` (self-hosted models, OpenRouter, etc.), mirroring `vision.py`'s existing pattern for Ingest — but explicitly deferred to keep v1's credential form and provider-list semantics simple (a fixed key-per-named-provider shape, no base-URL field). Revisit as a future-phase/roadmap item if real demand shows up; the adapter boundary in §2.2 means adding it later is additive, not a rework.
4. [06_TECH_STACK.md](../06_TECH_STACK.md) §2 and §5 get updated to add the `anthropic` dependency and remove the Model Playground TODO marker in the same change that actually adds the dependency to `requirements.txt` (per that document's own §4 rule) — i.e. during this phase's backend implementation task, not in this ADR.

## 3. Alternatives considered

- **Generic direct-HTTP client against each provider's REST API (no official SDKs):** rejected. The official SDKs already handle request signing, retries, and provider-specific error shapes; hand-rolling that for two providers duplicates effort the SDKs give for free, for no benefit specific to Forge's use case.
- **OpenAI only for v1, adding others later:** rejected as not meeting the phase's core mission — "compare providers side by side" needs at least two real providers to be worth building at all; a single-provider v1 would just be a thinner version of what Ingest's vision path already proves works.
- **A provider-agnostic abstraction library (e.g. LiteLLM or similar) instead of official SDKs per-provider:** considered, but rejected for v1 — it would be a third-party abstraction on top of the providers' own SDKs, adding a dependency whose own compatibility surface Forge would then be exposed to, for a phase that only needs two providers. Revisit if a third or fourth provider makes per-provider adapters genuinely repetitive.

## 4. Consequences

- **Easier:** future providers are additive (new adapter + credential provider enum value), not architectural changes, once the adapter boundary in §2.2 exists.
- **Harder / forecloses:** any provider not in the confirmed list is unavailable in v1 even if a user wants it — tracked as a roadmap item, not silently worked around with a generic HTTP fallback.
- **Touches:** [06_TECH_STACK.md](../06_TECH_STACK.md) (new dependency row(s) + §5 TODO resolved) and, if the "Custom / OpenAI-compatible" sub-question in §2.3 is answered yes, the credential schema shape decided in [ADR-0011](0011-model-playground-provider-credential-security.md) (would need an optional `base_url` field).
- Resolves the [06_TECH_STACK.md](../06_TECH_STACK.md) §5 TODO for Model Playground specifically (Prompt Studio's own TODO there is unaffected — Phase 03 was resolved to zero outbound calls and carries no provider dependency).

## 5. Cross-references

- [../06_TECH_STACK.md](../06_TECH_STACK.md)
- [../implementation/Phase-05-Model-Playground/01_SPEC.md](../implementation/Phase-05-Model-Playground/01_SPEC.md)
- [0011-model-playground-provider-credential-security.md](0011-model-playground-provider-credential-security.md)
- [README.md](README.md)
