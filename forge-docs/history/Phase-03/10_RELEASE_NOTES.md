# Prompt Studio — Release Notes

> **Purpose:** User-facing summary of what shipped in this phase, for `../../../docs/Roadmap.md`-style consumption once released.
> **Scope:** This phase only.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Content-complete. Finalized at the Released stage per `13_PHASE_LIFECYCLE.md`, after Release Candidate audit + Owner Sign-off.
> **Last Updated:** 2026-07-22

---

## Summary

Forge gains **Prompt Studio** (`/prompt-studio`): a workspace for authoring, versioning, and previewing reusable LLM prompts. A prompt is a body of text with named, typed variables (`${name}` placeholders); Prompt Studio renders a live, client-side preview of the substituted text, keeps every content edit as an immutable, restorable version, and lets a prompt be duplicated to seed a new one.

**This phase does not execute prompts against any LLM provider.** Prompt Studio is an authoring and versioning tool, not an execution tool — there are no outbound network calls, no provider concepts, and no API-key storage anywhere in this phase. Live execution against a real model is explicitly deferred to a future phase.

## What's new

- A new `/prompt-studio` page: a searchable, tag-filterable list of saved prompts alongside an editor for the selected one.
- **Structured variables**: each variable has a name, a type (string/number/boolean), a required flag, an optional default, and an optional description.
- **Client-side render preview**: type or accept default values for each variable and see the fully-substituted prompt update live — this never leaves the browser and never calls any backend endpoint.
- **Immutable version history**: every change to a prompt's body or variables becomes a new, permanent version. Nothing is ever lost, and version numbers only ever move forward.
- **Diff between versions**: pick any two versions to see exactly what changed, line by line.
- **Restore**: bring back an old version's content as the new current version — a fresh version, not a rewrite of history.
- **Duplicate**: clone a prompt to seed a new one — this is Prompt Studio's "reusable template" mechanism; any saved prompt already doubles as a starting point for the next one.
- Reachable from the sidebar, the command palette, and the Workbench's pinned-tools panel (which previously showed Prompt Studio as "Coming soon").
- Every create, edit, restore, duplicate, and delete appears in the existing Recent Activity feed, with no changes to that feed's own code.

## Out of scope (by design, not oversight)

- **Live execution against a real LLM provider.** No outbound network calls, no provider SDK, no API-key concept. This was the central scope decision of this phase, made explicitly with the project owner rather than assumed — see [`01_SPEC.md`](01_SPEC.md) §4–§5.
- A separate "Template" entity distinct from "Prompt" — Duplicate covers this.
- Folders or nested organization beyond tags.
- Import/export or multi-user sharing (Forge is single-tenant).

## Known limitations

Five items are tracked as QA tickets rather than claimed as fully tested, since this session's environment could not exercise them reliably: real human keyboard typing directly into the Monaco body editor; Escape-to-close and focus-trap behavior for confirmation dialogs under a genuine trusted user gesture; pixel-level screenshots of dark mode and the mobile/responsive layout; the Copy action's success-path toast specifically; and high-DPI display scaling. None of these reflect a known defect — see [`CURRENT_STATE.md`](CURRENT_STATE.md) Known Issues for the full detail on why each is environment-limited rather than untested by choice.

## Cross-references

- [../../implementation/Phase-03-Prompt-Studio/01_SPEC.md](../../implementation/Phase-03-Prompt-Studio/01_SPEC.md)
- [../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md](../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md)
- [../../implementation/Phase-03-Prompt-Studio/RC1_AUDIT.md](../../implementation/Phase-03-Prompt-Studio/RC1_AUDIT.md)
- [../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md)
- [QA/README.md](QA/README.md)
