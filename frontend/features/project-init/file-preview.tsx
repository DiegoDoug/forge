"use client";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { AI_INSTRUCTIONS_FILES, type TemplateKind, type TemplateKindInfo } from "./api";

const FDK_FILE_DESCRIPTIONS: Record<string, string> = {
  "README.md": "Objective, scope, deliverables, milestones.",
  "CURRENT_STATE.md": "Live status snapshot, updated at every checkpoint.",
  "01_SPEC.md": "Functional specification.",
  "02_UI.md": "Screen-level UI specification.",
  "03_BACKEND.md": "Backend service design.",
  "04_DATABASE.md": "Schema and migration plan.",
  "05_COMPONENTS.md": "Frontend component breakdown.",
  "06_API.md": "Endpoint contracts.",
  "07_TESTING.md": "Test plan.",
  "08_ACCEPTANCE.md": "Pass/fail acceptance criteria.",
  "09_IMPLEMENTATION_TASKS.md": "Ordered task list.",
  "10_RELEASE_NOTES.md": "User-facing summary of what shipped.",
  "IMPLEMENT.md": "Execution contract for the phase.",
};

const AI_FILE_DESCRIPTIONS: Record<string, string> = {
  "CLAUDE.md": "Instructions for Claude Code.",
  "AGENTS.md": "Instructions for agent-based coding tools.",
  "instructions.md": "Generic, tool-agnostic instructions file.",
};

/** Lists the filenames a kind will produce, with a one-line description each
 * - a sanity-check disclosure, not a byte-for-byte rendered preview (that
 * would require duplicating the backend renderer's template logic in
 * TypeScript; see 05_COMPONENTS.md). For ai_instructions this always shows
 * all three possible files rather than tracking the form's checkbox
 * selection live, keeping this component decoupled from form state. */
export function FilePreview({ kind, catalog }: { kind: TemplateKind; catalog: TemplateKindInfo[] }) {
  const info = catalog.find((k) => k.kind === kind);
  const files = kind === "fdk_phase" ? (info?.output_files ?? []) : [...AI_INSTRUCTIONS_FILES];
  const descriptions = kind === "fdk_phase" ? FDK_FILE_DESCRIPTIONS : AI_FILE_DESCRIPTIONS;

  if (files.length === 0) return null;

  return (
    <Accordion>
      <AccordionItem value="preview">
        <AccordionTrigger className="text-sm">Preview files ({files.length})</AccordionTrigger>
        <AccordionContent>
          <ul className="flex flex-col gap-1.5">
            {files.map((file) => (
              <li key={file} className="flex items-baseline justify-between gap-3">
                <code className="font-mono text-xs">{file}</code>
                <span className="text-right text-xs text-muted-foreground">{descriptions[file] ?? ""}</span>
              </li>
            ))}
          </ul>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
