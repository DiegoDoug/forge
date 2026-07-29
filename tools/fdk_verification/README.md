# fdk_verification

Milestone 1 implementation of the Autonomous Multi-Agent Verification Framework specified in [`forge-docs/15_VERIFICATION_FRAMEWORK.md`](../../forge-docs/15_VERIFICATION_FRAMEWORK.md), built per [`forge-docs/templates/prompts/VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md`](../../forge-docs/templates/prompts/VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md).

**Status: Milestones 1–3 — no autonomous behavior yet.** Nothing in this package hooks into an FDK phase or auto-continues anything; that's Milestone 4. It provides:

- `contract.py` — parses a `VERIFICATION_CONTRACT.md` (per [`VERIFICATION_CONTRACT_TEMPLATE.md`](../../forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md)) into a `VerificationContract`, and validates it — fails loudly on a missing required section or an unrecognized verifier name.
- `report.py` — the `VerificationReport` model, PASS/FAIL aggregation, and Markdown rendering matching §6's format. Testable from hand-constructed verifier results, independent of any real verifier.
- `verifier.py` — the `Verifier` protocol every verifier and both Orchestrators communicate through.
- `orchestrator.py` — a generic, contract-driven verifier-invocation loop with zero verifier-specific logic, per §9's "Orchestrator-replaceable" principle. A single verify-once-and-aggregate pass — no retry or escalation logic lives here.
- `verifiers/` — the 8 concrete verifiers (Specification, Architecture, Build, Test, Regression, Code Quality, Documentation, UX), each independently constructible/runnable, none importing any other, each delegating to a real tool (git, a contract-declared shell command) where one exists rather than reimplementing it. `verifiers.default_registry()` builds one instance of each, keyed by canonical name.
- `repair_loop.py` — `RepairLoop`, capped at 3 cycles per §7. Decoupled from `Orchestrator`: it takes any zero-argument callable returning a `VerificationReport`, so it works identically over the real Orchestrator, the reference one below, or a test stub. Never repairs anything itself — `on_remediation` is a notification hook for whatever external mechanism (a Claude Code session, eventually) performs the actual repair.
- `escalation.py` — the 6 §8 conditions. `evaluate()` auto-detects retry-limit-exceeded and confidence-below-threshold mechanically, plus a recurring-identical-Architecture-failure heuristic; the other 3 (ambiguous requirements, destructive operation required, blocked external dependency) are judgment calls an external caller raises directly — this module never invents them from a report alone.
- `reference_orchestrator.py` — `ReferenceOrchestrator`, a from-scratch second implementation of the same coordination role (different internal shape, its own exception type, zero shared code with `orchestrator.py`) — the concrete proof, not just an assertion, that the 8 verifiers need no change to run under a different orchestrator.

Known, documented limitations of the Milestone 2 verifiers (not bugs — generic tooling can't do more than this without app-specific hooks that don't exist yet): Specification and Regression are attestation-based (they check the contract's own checkboxes, not live app behavior); Architecture only checks file-scope boundaries, not circular imports or duplicated services; Documentation only checks whether a backticked path was actually touched; Code Quality only ever warns, never fails; UX always reports N/A (no browser automation is wired up). Each verifier's module docstring explains its specific scope.

Not here yet, by design: FDK phase-lifecycle integration, automatic contract discovery, and auto-continue-on-PASS (Milestone 4) — gated by a real end-to-end dry run against an actual phase before it's considered done.

## Running the tests

From the repository root, using `backend/.venv` (already has pytest via `requirements-dev.txt` — no new dependency needed for this package):

```bash
backend/.venv/Scripts/python.exe -m pytest tools/tests -v
```

`tools/conftest.py` puts `tools/` on `sys.path` so `fdk_verification` is importable without installation — this package is standalone dev tooling, not a Forge application dependency, and intentionally uses only the Python standard library (no new entry in [`06_TECH_STACK.md`](../../forge-docs/06_TECH_STACK.md) needed).
