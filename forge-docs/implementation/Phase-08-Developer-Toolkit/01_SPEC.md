# Developer Toolkit — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved in principle by the project owner 2026-08-05 — scope, route, navigation identity, top-level tab architecture, Utilities frontend-only conclusion, and no-backend-abstraction decision all approved; §7's open questions all resolved; requested corrections applied. Awaiting explicit implementation authorization ([`IMPLEMENT.md`](IMPLEMENT.md)). See Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md).
> **Version:** 0.2.0
> **Last Updated:** 2026-08-05
> **Depends On:** [../../00_VISION.md](../../00_VISION.md), [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md), [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
> **Supersedes:** v0.1 template placeholder of this document.

---

## 1. Summary

Developer Toolkit unifies Forge's three existing, already-shipped, already-independently-consolidated tool pages — **Generators** (`/generators`), **Crypto** (`/crypto`), and **Utilities** (`/utilities`) — behind **one page and one nav entry**. Each of the three is already a single, internally-coherent page today (unlike Converters/Ingest before Phase 04, which were two separate multi-tool surfaces); this phase's job is purely to fold three sidebar entries into one, not to reorganize what's inside any of them.

**This phase is a navigation/presentation consolidation, not a service or capability change.** Every generator, crypto operation, and utility a user can run today remains runnable, byte-for-byte unchanged in behavior, after this phase ships. Nothing in `backend/app/services/generators/`, `backend/app/services/crypto/`, or any of the four Utilities tool components (`checksum-tool.tsx`, `color-tool.tsx`, `qr-tool.tsx`, `timezone-tool.tsx` — all pure client-side, `crypto.subtle`/browser-API based, with **no backend counterpart at all**) is modified.

This phase is deliberately **smaller in shape than Phase 04 (Universal Converter)**, its closest precedent. Universal Converter introduced a `ConverterProvider` backend abstraction because the roadmap already signaled a *future* need (new conversion directions arriving as new providers). No equivalent forward-looking signal exists for Developer Toolkit anywhere in `forge-docs/` — Generators, Crypto, and Utilities are each a fixed, closed set of tools, not an extensible provider surface. Per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) (don't design for hypothetical future requirements), this phase introduces **no new backend abstraction**. See §4 and [`03_BACKEND.md`](03_BACKEND.md) for the full reasoning.

Three scope questions, resolved during this specification pass from direct repository inspection (recorded here rather than left open, per the project owner's specification-session instructions of 2026-08-05):

1. **Consolidation-first, presentation layer only** — mirrors Universal Converter's resolved scope question 1, for the same reason.
2. **Utilities requires zero backend work.** Investigated directly (see §6 below and [`03_BACKEND.md`](03_BACKEND.md) §1): all four Utilities tools run entirely in the browser. There is no `backend/app/services/utilities/`, no `backend/app/api/routes/utilities.py`, no Utilities schema file — and none is needed.
3. **Single unified page**, replacing three existing nav entries (Generators, Crypto, Utilities) with one — see [`02_UI.md`](02_UI.md) §2.

## 2. User stories

- As a Forge user who reaches for a generated password, a hash, and a QR code in the same session, I want all three under one "Developer Toolkit" nav entry, so I'm not scanning three separate sidebar rows for tools that are all, conceptually, "small dev utilities."
- As a returning user with `/generators`, `/crypto`, or `/utilities` bookmarked, I want my bookmark to keep working, so consolidating the sidebar doesn't quietly break a link I've saved.
- As a keyboard-driven user, I want one command-palette entry and one shortcut for the unified page, so I'm not choosing between three overlapping entries that all lead to "developer tools."
- As a user who already knows the Crypto page's internal AES/JWT/RSA-ECC tabs, or the Generators/Utilities pages' tool grids, I want those exact same layouts and interactions preserved inside the unified page, unchanged — no relearning.
- As the project owner, I want this consolidation to touch as little surface area as possible — no new backend abstraction, no schema change — because nothing about Generators/Crypto/Utilities signals a need for one, unlike Universal Converter's provider registry.

## 3. Functional requirements

1. A single page at **`/developer-toolkit`** presents three sections — **Generators**, **Crypto**, **Utilities** — as top-level tabs (see [`02_UI.md`](02_UI.md) §1 for the tabs-vs-stacked-sections decision and why this differs from Universal Converter's stacked-section layout). Each section presents that area's existing feature components with their current configuration, ordering, and structure preserved, and with zero modification to the components themselves:
   - **Generators** tab: `PasswordGenerator`, `UuidGenerator`, `NanoIdGenerator`, `RandomBytesGenerator`, `ApiKeyGenerator`, `JwtSecretGenerator`, `EntropyEstimator` — the same seven components, same grid, unmodified.
   - **Crypto** tab: the existing `Tabs` (Encode & Hash / AES / JWT / RSA & ECC) exactly as `frontend/app/(app)/crypto/page.tsx` renders them today, nested unmodified inside the new top-level Crypto tab.
   - **Utilities** tab: `QrTool`, `ColorTool`, `TimezoneTool`, `ChecksumTool` — the same four components, same grid, unmodified.
2. The three old routes redirect (Next.js `redirects()` in `next.config.ts`, `permanent: false` — matching the precedent set by `/vault` → `/secrets` and `/ingest` → `/converters`) rather than 404ing:
   - `/generators` → `/developer-toolkit?tab=generators`
   - `/crypto` → `/developer-toolkit?tab=crypto`
   - `/utilities` → `/developer-toolkit?tab=utilities`
   The `?tab=` query param preselects the matching top-level tab on load, so a bookmark to `/crypto` still lands the user directly on the Crypto tools rather than defaulting to Generators.
3. `frontend/lib/nav-registry.ts`'s three entries (`Generators` / shortcut `G`, `Crypto` / shortcut `C`, `Utilities` / shortcut `U`) are replaced by **one** entry — "Developer Toolkit", href `/developer-toolkit`, icon `Wrench`, shortcut `U` (all confirmed by the project owner 2026-08-05; see [`02_UI.md`](02_UI.md) §2). The command palette (`cmdk`) reads from the same `NAV_ITEMS` registry, so this one change updates both surfaces per [`04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §2.
4. `backend/app/services/workbench.py`'s `WORKBENCH_TOOL_KEYS` catalog merges its three existing keys (`"generators"`, `"crypto"`, `"utilities"`) into one (`"developer_toolkit"`), mirroring the exact precedent Universal Converter set when it merged `"ingest"`/`"universal_converter"` into `"converters"` (Phase 04, Milestone 5). None of the three retired keys appears in `DEFAULT_PINNED_TOOLS` today, so no default-pin migration is needed. `frontend/features/workbench/tool-metadata.ts`'s `NAV_KEY_BY_HREF` map is updated to match (three entries collapse to one, keyed off the new nav-registry href).
5. `frontend/features/workbench/components/quick-actions-panel.tsx`'s "Generate password" quick action updates its `href` from `/generators` to `/developer-toolkit?tab=generators` (the redirect from requirement 2 would also satisfy this, but pointing directly at the new URL avoids an unnecessary redirect hop on a frequently-used action).
6. Every generator, crypto, and utility operation available today remains available, unchanged in behavior: no component under `frontend/features/generators/`, `frontend/features/crypto/`, or `frontend/features/utilities/` is modified, and no backend route/service under `backend/app/api/routes/generators.py`, `backend/app/api/routes/crypto.py`, `backend/app/services/generators/`, or `backend/app/services/crypto/` is touched.
7. The existing `/api/generators/*` and `/api/crypto/*` endpoints continue to work, unchanged, at their current paths — this phase adds no new endpoint and removes none (see [`06_API.md`](06_API.md)).
8. No new external dependency is introduced (per [`06_TECH_STACK.md`](../../06_TECH_STACK.md) §4) — this phase is a page/routing restructure using components and libraries already in use.
9. All existing security properties carry over unchanged: session-auth requirement on every Generators/Crypto route (`AuthDep`), no new attack surface (see [`03_BACKEND.md`](03_BACKEND.md) §4).

## 4. Relationship to existing features

Consolidates, at the presentation and navigation layer only:

- **Generators** (`frontend/features/generators/`, `backend/app/api/routes/generators.py`, `backend/app/services/generators/`) — the seven existing components move under the new unified page's Generators tab, unmodified. Backend untouched.
- **Crypto** (`frontend/features/crypto/`, `backend/app/api/routes/crypto.py`, `backend/app/services/crypto/`) — the existing page (itself already internally tabbed) moves under the new unified page's Crypto tab, unmodified, including its own nested tab structure. Backend untouched.
- **Utilities** (`frontend/features/utilities/`) — the four existing, entirely client-side components move under the new unified page's Utilities tab, unmodified. There is no backend counterpart to touch.

No existing table, model, or unrelated feature (Secrets, Notes, Documents, Converters, Knowledge, Projects) is modified. Unlike Universal Converter, **no new backend abstraction is introduced** — see §1 and [`03_BACKEND.md`](03_BACKEND.md) §1 for why a provider-style registry is not justified here.

## 5. Explicitly out of scope

- **Rewriting Generator or Crypto service logic.** `backend/app/services/generators/service.py` and `backend/app/services/crypto/service.py` are not touched.
- **Changing cryptographic algorithms or generator behavior.** Every algorithm, parameter, and default stays exactly as shipped.
- **Creating a new Utilities backend service.** Investigated directly (§6) — none of the four Utilities tools needs one, and none is created.
- **Changing any public API contract.** `/api/generators/*` and `/api/crypto/*` keep their current paths, request/response shapes, and auth requirements.
- **Any database migration.** This phase introduces no new table, column, or persisted state — see [`04_DATABASE.md`](04_DATABASE.md).
- **New developer-tool functionality.** Specifically, per `docs/Roadmap.md`'s "Near-term" section: deep-linking the command palette directly into a *specific tool's pre-filled state* (e.g. "jump straight to the JWT tool with a token pre-filled") and a standalone "Hash Compare" Utilities tool are both real, already-tracked gaps — **neither is delivered by this phase**. This phase's `?tab=` redirect param (requirement 2) selects the right *section*, not a specific tool's pre-filled state; that remains the tracked near-term gap, unchanged by this phase.
- **Unrelated frontend redesign.** No visual/design-system change beyond what's structurally required to nest three existing pages' content under one set of tabs.
- **Promoting `WORKBENCH_TOOL_KEYS`/`NAV_KEY_BY_HREF`'s documented manual-sync gap (`03_BACKEND.md` §3 note) into an automated registry.** [ADR-0008](../../decisions/0008-capability-registry-direction.md) already covers this direction and is explicitly deferred until a second real registry-shaped need exists — this phase is not that trigger.

## 6. Utilities backend investigation

Per this specification session's instructions, investigated directly rather than assumed:

- `find backend/app -iname "*util*"` and a repository-wide grep for `utilities`/`checksum`/`qr_code`/`timezone` inside `backend/app/{api,services,schemas}` returned **no matches** other than unrelated `.pyc` cache noise.
- All four components in `frontend/features/utilities/` (`checksum-tool.tsx`, `color-tool.tsx`, `qr-tool.tsx`, `timezone-tool.tsx`) were inspected; none contains a `fetch(`, API client call, or `/api/` reference. `checksum-tool.tsx` uses the browser's native `crypto.subtle.digest` (Web Crypto API) directly.
- **Conclusion: Utilities is, and remains, entirely frontend-only.** No backend route, service, or schema exists for it today, and this phase creates none. Developer Toolkit is implementable for the Utilities section through frontend/navigation consolidation alone.

## 7. Open questions

**All resolved by the project owner on 2026-08-05**, during the same specification session that drafted this document:

- [x] **Route slug and nav label** — confirmed as proposed: route `/developer-toolkit`, label "Developer Toolkit". Consistent with existing kebab-case multi-word routes (`/project-init`, `/prompt-studio`, `/model-playground`). A shorter `/toolkit` slug was offered and declined. See [`02_UI.md`](02_UI.md) §2.
- [x] **Icon and shortcut** — confirmed as proposed: keep `Wrench` (Utilities' current icon, reads most generically as "toolkit") and shortcut `U`; free `Wand2`/`G` and `ShieldHalf`/`C`. An alternative shortcut `D` was offered and declined (it currently belongs to Workbench and would have required a reassignment).
- [x] **Tabs vs. Universal Converter's stacked-section layout** — confirmed as proposed: **top-level tabs** (§3 requirement 1), with Crypto's existing nested tab set sitting one level inside its top-level tab. Stacked sections (Phase 04's layout) were offered and declined: stacking three sections where one is itself already tabbed reads unevenly, whereas Universal Converter's two sections were both flat grids. See [`02_UI.md`](02_UI.md) §1.

No open question remains against this specification. What still gates implementation is the separate, explicit authorization step described in [`IMPLEMENT.md`](IMPLEMENT.md) and [`CURRENT_STATE.md`](CURRENT_STATE.md) — the project owner has asked to review the drafted Phase 08 documents before implementation begins.

## 8. TODO

- [x] Project-owner review of this filled-in spec, plus [`02_UI.md`](02_UI.md), [`03_BACKEND.md`](03_BACKEND.md), [`04_DATABASE.md`](04_DATABASE.md), and [`06_API.md`](06_API.md) — **approved in principle 2026-08-05**, with three requested corrections applied to [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) and [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).
- [ ] Explicit implementation authorization, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) "Specification → Authorized" — not yet given; see [`IMPLEMENT.md`](IMPLEMENT.md)'s Status line. This is the sole remaining gate on this phase.

## 9. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
- [../Phase-04-Universal-Converter/01_SPEC.md](../Phase-04-Universal-Converter/01_SPEC.md) — closest precedent phase
- [../../../docs/Roadmap.md](../../../docs/Roadmap.md) — near-term gaps explicitly not delivered by this phase
