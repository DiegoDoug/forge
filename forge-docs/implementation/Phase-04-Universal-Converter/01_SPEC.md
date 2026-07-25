# Universal Converter — Spec

> **Purpose:** The functional specification for this phase — what it does, from a user's perspective, in enough detail to build from.
> **Scope:** Functional behavior only. UI layout detail lives in 02_UI.md; data model detail lives in 04_DATABASE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — specification session in progress (Discovery complete, scope decisions confirmed with project owner 2026-07-23; pending final owner sign-off before `IMPLEMENT.md` is authorized). See Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md).
> **Version:** 0.2.0
> **Last Updated:** 2026-07-23
> **Depends On:** [../../00_VISION.md](../../00_VISION.md), [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md), [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
> **Supersedes:** v0.1 template placeholder of this document.

---

## 1. Summary

Universal Converter unifies Forge's two existing, currently-separate conversion surfaces — **Converters** (nine client-side text/data tools: JSON, YAML, XML, CSV, regex, URL/Unicode, cron, diff, timestamp) and **Ingest** (server-side, job-based any-file→Markdown conversion via MarkItDown, with optional vision-LLM assist for scanned PDFs) — behind one page, one nav entry, and one architectural concept: a **converter provider**.

**This phase is a consolidation, not an expansion of conversion capability.** Every conversion a user can perform today remains possible, unchanged in behavior, after this phase ships. What changes is presentation (one page instead of two) and backend shape (a provider registry replaces ad hoc dispatch), so that a *future* phase can add a genuinely new conversion direction (e.g. Markdown → DOCX, server-side format round-trips) by registering one new provider rather than re-architecting the surface. See §5 for what is explicitly deferred, and [`03_BACKEND.md`](03_BACKEND.md) §1 for why the provider abstraction is scoped in now even though no new provider ships this phase.

Four scope questions were raised to the project owner during specification and resolved as follows (see [`CURRENT_STATE.md`](CURRENT_STATE.md) Session Notes for the record):

1. **Consolidation-first**, not a full universal any→any converter, this phase.
2. Client-side text converters (JSON/YAML/XML/CSV/regex/URL/Unicode/timestamp/diff) **stay client-side** — no migration to a backend round-trip.
3. **Single unified page** replaces the two existing nav entries (Converters, Ingest).
4. **No new database persistence** — file-based conversion stays exactly as ephemeral (in-memory job store, disk scratch, TTL cleanup) as it is today.

## 2. User stories

- As a Forge user who reaches for both a text tool (e.g. JSON formatting) and file conversion (e.g. a PDF → Markdown) in the same session, I want both under one page, so I don't have to remember which of two separate nav entries has the tool I need.
- As a returning user with `/ingest` or `/converters` bookmarked, I want my bookmark to keep working, so consolidating the UI doesn't quietly break a link I've saved.
- As a keyboard-driven user, I want a single command-palette entry and shortcut for the unified page, so I'm not choosing between two overlapping entries that do conceptually the same job.
- As a user converting a batch of documents to Markdown, I want the exact same upload/progress/preview/download/save-to-notes workflow Ingest already gives me today, unchanged, just reached from the unified page.
- As a user formatting JSON or diffing two blocks of text, I want the exact same instant, offline, client-side behavior I have today — no upload, no network round-trip, no change in speed.
- As the project owner planning future phases, I want this phase to leave a clean extension point (a provider interface) so that a later phase adding a new conversion direction doesn't need to re-architect the page or the API surface.

## 3. Functional requirements

1. A single page at `/converters` (URL unchanged from today's Converters page — see [`02_UI.md`](02_UI.md) §1 for why this URL is kept rather than introduced fresh) presents two sections: **Text & Data** (the nine existing client-side tools, unmodified) and **Documents** (the existing Ingest dropzone/job-list/preview-sheet workflow, unmodified in behavior).
2. The old `/ingest` route redirects (HTTP/Next.js redirect, not a 404) to `/converters` so existing bookmarks and shared links keep working, per the aliasing precedent in [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md).
3. `frontend/lib/nav-registry.ts`'s two entries (`Converters` / shortcut `O`, `Ingest` / shortcut `I`) are replaced by one entry — see [`02_UI.md`](02_UI.md) §2 for the exact label/icon/shortcut proposal.
4. Every conversion capability available today remains available, byte-for-byte unchanged in output, after this phase: the nine client-side tools' logic is not touched, and the Ingest pipeline (MarkItDown + vision fallback + postprocess cleanup) is not touched — it is *wrapped*, not rewritten. See [`03_BACKEND.md`](03_BACKEND.md) §1–§2.
5. The existing `/api/ingest/*` endpoints and `/api/converters/cron/parse` continue to work, unchanged, at their current paths — this phase adds new endpoints alongside them, it does not remove or rename existing ones (no breaking API changes; see [`06_API.md`](06_API.md)).
6. A new backend `ConverterProvider` interface (see [`03_BACKEND.md`](03_BACKEND.md) §1) formalizes "what a file-conversion capability is" — declared input extensions, declared output format, and a `convert(...)` entry point. The existing MarkItDown/vision pipeline is registered as the first (and, this phase, only) provider. This is additive scaffolding, not a new user-facing capability.
7. A new endpoint (see [`06_API.md`](06_API.md)) exposes the registered providers and their declared formats, so the unified frontend page can render its "Documents" section's supported-format list from the same source of truth the backend uses, rather than a duplicated hardcoded list (today, `KNOWN_EXTENSIONS` in `formats.py` is that source of truth; this requirement makes it reachable over the API instead of only via `/api/ingest/formats`, which continues to work as today for backward compatibility).
8. All existing security properties carry over unchanged: filename sanitization, upload size/count caps, session-auth requirement on every route, generic error envelopes (see [`03_BACKEND.md`](03_BACKEND.md) §4 and [`06_API.md`](06_API.md) §3).
9. No new external dependency is introduced (per [`06_TECH_STACK.md`](../../06_TECH_STACK.md) §4) — the provider registry is plain Python composition over existing code.

## 4. Relationship to existing features

Consolidates, at the presentation and backend-organization layer only:

- **Converters** (`frontend/features/converters/`, `backend/app/services/converters/`, `backend/app/api/routes/converters.py`) — the nine client-side tool components are moved under the new unified page but are not modified. `services/converters/cron.py` and its route are untouched; `services/converters/` gains a new `providers/` submodule (the registry — see [`03_BACKEND.md`](03_BACKEND.md) §1).
- **Ingest** (`frontend/features/ingest/`, `backend/app/services/ingest/`, `backend/app/api/routes/ingest.py`) — the dropzone/job-list/preview-sheet components move under the unified page's "Documents" section but are not modified. `services/ingest/` itself is not renamed or restructured; it is wrapped by one new provider module in `services/converters/providers/`, per the "prefer extending an existing subpackage for consolidation phases" guidance in [`03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §3.

No existing table, model, or unrelated feature (Documents, Notes, Secrets) is modified. The existing `save-to-notes` bridge from Ingest (`backend/app/api/routes/ingest.py` calling `notes_service.create_note`) is preserved exactly as-is — it is the established precedent for a converter reaching into another feature's service layer for a save action, and this phase does not change that pattern or add a new one.

## 5. Explicitly out of scope

- **Any new conversion direction.** No Markdown→DOCX/PDF, no server-side JSON↔YAML↔XML round-trips, no image format conversion beyond what MarkItDown already extracts as text. Confirmed with the project owner during specification (2026-07-23) as "consolidation-first" — seen §1. A new conversion direction is a new provider registered in a later phase, not a silent scope-add here.
- **Moving the client-side text converters to the backend.** Confirmed with the project owner — they stay client-side; only the presentation layer unifies.
- **New database persistence** (conversion history, presets, saved conversion settings). Confirmed with the project owner — file-based conversion keeps Ingest's exact ephemeral, TTL-cleaned, non-persisted model. See [`04_DATABASE.md`](04_DATABASE.md).
- **The Documents feature's rich-text export pipeline** (`backend/app/services/documents/export.py`, txt/md/xml/doc/docx/pdf). This is a one-directional generator from the rich-text editor's own HTML content, not a general file-conversion capability, and is explicitly Phase 07 (Knowledge Hub) territory per [`02_ROADMAP.md`](../../02_ROADMAP.md) — not touched, shared, or refactored by this phase.
- **A generalized "any format to any format" matrix UI** (e.g. a format-picker grid). The unified page keeps today's two-section layout (Text & Data, Documents); a richer format-matrix UI is only worth building once more than one provider exists, per [`01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) (don't design for hypothetical future requirements).
- **Renaming or restructuring `services/ingest/` internals** (`converter.py`, `jobs.py`, `vision.py`, `postprocess.py`, `formats.py`). These are wrapped by a thin provider adapter, not touched, minimizing risk to an already-working pipeline.
- **Rate limiting or new upload-abuse protections** beyond what exists today — no new attack surface is introduced (no new conversion directions, no new persistence), so the existing deployment-level posture documented in [`../../../docs/Security.md`](../../../docs/Security.md) is unchanged and sufficient.

## 6. Open questions

None remaining. The four scope questions that would otherwise block finalizing this spec were raised to the project owner directly during this specification session and resolved as recorded in §1 above — see Session Notes in [`CURRENT_STATE.md`](CURRENT_STATE.md) for the record of that exchange.

## 7. TODO

- [ ] Project-owner review of this filled-in spec, plus [`02_UI.md`](02_UI.md), [`03_BACKEND.md`](03_BACKEND.md), [`04_DATABASE.md`](04_DATABASE.md), and [`06_API.md`](06_API.md) — required before `08_ACCEPTANCE.md` and `09_IMPLEMENTATION_TASKS.md` are drafted (Stage 4) and before `IMPLEMENT.md` can be authorized, per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) "Specification → Authorized."

## 8. Cross-references

- [README.md](README.md)
- [02_UI.md](02_UI.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../01_PRODUCT_PRINCIPLES.md](../../01_PRODUCT_PRINCIPLES.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
