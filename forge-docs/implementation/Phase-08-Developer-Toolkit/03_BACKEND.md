# Developer Toolkit — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved in principle by the project owner 2026-08-05 — the no-backend-abstraction decision and Utilities frontend-only conclusion are both confirmed.
> **Last Updated:** 2026-08-05

---

## 1. Service boundary

**No new `services/<name>/` subpackage, and no extension of an existing one's business logic.** This is the deliberate outcome of investigating the question, not a default assumption:

- `backend/app/services/generators/service.py` and `backend/app/services/crypto/service.py` (plus their routes `backend/app/api/routes/generators.py`, `backend/app/api/routes/crypto.py`, and schemas `backend/app/schemas/generators.py`, `backend/app/schemas/crypto.py`) already exist, are stable, and are **not modified** by this phase.
- Utilities has **no backend module today** (`backend/app/api/routes/`, `backend/app/services/`, and `backend/app/schemas/` all confirmed to have zero Utilities-related files — checksum/QR/color/timezone logic is entirely `frontend/features/utilities/`, using the browser's native Web Crypto API for hashing). This phase creates none, per [`01_SPEC.md`](01_SPEC.md) §6's investigation.

The **only** backend file this phase touches is `backend/app/services/workbench.py` — and that is a catalog-dict edit, not new service logic: `WORKBENCH_TOOL_KEYS`'s three existing keys (`"generators"`, `"crypto"`, `"utilities"`) merge into one (`"developer_toolkit"`). This mirrors, file-for-file, the exact edit Universal Converter made to the same dict in its own Milestone 5 (merging `"ingest"`/`"universal_converter"` into `"converters"`) — see the existing code comment at `backend/app/services/workbench.py` lines 18–28 documenting that precedent.

[`03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §3 explicitly names this phase as a case where extending, not adding, is the default ("Prefer extending an existing subpackage for consolidation phases like **Developer Toolkit** / Universal Converter") — this phase satisfies that guidance by needing to extend nothing at all in the business-logic layer, since none of the three areas' logic changes.

## 2. Business logic

None introduced. No new operation, computation, or business rule is added anywhere in the backend by this phase.

## 3. Integration with existing services

None beyond the workbench catalog edit described in §1. Generators and Crypto's services are not called into by any new code; Utilities has nothing to integrate with (it isn't backend-resident).

## 4. Architectural compliance

- [x] Routers stay thin — unaffected, since no router is touched beyond the workbench catalog dict (not a router).
- [x] No cross-feature imports introduced — the new frontend page composes existing feature *components*, which is the page layer's normal role (see [`05_COMPONENTS.md`](05_COMPONENTS.md) §3), not a features-importing-features violation; no backend cross-feature import occurs at all, since no backend service is modified.
- [x] No new external dependency — confirmed nothing in this phase requires one; [`06_TECH_STACK.md`](../../06_TECH_STACK.md) unaffected.

## 5. TODO

- [ ] None outstanding for this document specifically — flagged complete pending the same overall project-owner review noted in [`01_SPEC.md`](01_SPEC.md) §8.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
