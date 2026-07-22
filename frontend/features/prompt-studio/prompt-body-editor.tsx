"use client";

import Editor, { type Monaco, type OnMount } from "@monaco-editor/react";
import { useTheme } from "next-themes";
import { useCallback, useEffect, useRef } from "react";

const PLACEHOLDER_MATCH = /\$\$|\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}/g;

/** Plain-text Monaco editor for a prompt body. Highlights every ${name}
 * token: green if it's a declared variable, amber if it references a name
 * that isn't declared yet (the same condition that produces a save-time 422
 * per 01_SPEC.md §3.4) - so the editor surfaces the problem before the user
 * even attempts to save. */
export function PromptBodyEditor({
  value,
  onChange,
  declaredNames,
}: {
  value: string;
  onChange: (value: string) => void;
  declaredNames: string[];
}) {
  const { resolvedTheme } = useTheme();
  const monacoRef = useRef<Monaco | null>(null);
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const decorationIdsRef = useRef<string[]>([]);

  const applyDecorations = useCallback(() => {
    const monaco = monacoRef.current;
    const editor = editorRef.current;
    if (!monaco || !editor) return;
    const model = editor.getModel();
    if (!model) return;

    const declared = new Set(declaredNames);
    const decorations: import("monaco-editor").editor.IModelDeltaDecoration[] = [];
    const text = model.getValue();

    for (const match of text.matchAll(PLACEHOLDER_MATCH)) {
      if (match[0] === "$$") continue;
      const name = match[1] ?? match[2];
      if (!name || match.index === undefined) continue;
      const start = model.getPositionAt(match.index);
      const end = model.getPositionAt(match.index + match[0].length);
      decorations.push({
        range: new monaco.Range(start.lineNumber, start.column, end.lineNumber, end.column),
        options: {
          inlineClassName: declared.has(name) ? "prompt-var-declared" : "prompt-var-undeclared",
        },
      });
    }

    decorationIdsRef.current = editor.deltaDecorations(decorationIdsRef.current, decorations);
  }, [declaredNames]);

  const handleMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    applyDecorations();
    // `automaticLayout` relies on a ResizeObserver that isn't guaranteed to
    // fire before the surrounding flex layout has settled on first paint -
    // force one explicit re-measurement against the (by-then-stable) real
    // container size, so the editor never gets stuck at Monaco's initial
    // near-zero fallback. setTimeout, not requestAnimationFrame: rAF is tied
    // to the compositor and can be starved in a backgrounded/non-visible tab.
    setTimeout(() => editor.layout(), 0);
  };

  // Re-decorate when the declared-variable set changes (e.g. a variable was
  // added/removed/renamed) even though the body text itself didn't change.
  useEffect(() => {
    applyDecorations();
  }, [applyDecorations]);

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <style>{`
        .prompt-var-declared { color: var(--color-emerald-600, #059669); font-weight: 600; }
        .prompt-var-undeclared { color: var(--color-destructive, #e11d48); font-weight: 600; text-decoration: underline wavy; }
      `}</style>
      <Editor
        height="280px"
        language="plaintext"
        theme={resolvedTheme === "dark" ? "vs-dark" : "light"}
        value={value}
        onMount={handleMount}
        onChange={(next) => {
          onChange(next ?? "");
          // Re-apply after the model updates on the next tick.
          setTimeout(applyDecorations, 0);
        }}
        options={{
          minimap: { enabled: false },
          wordWrap: "on",
          fontSize: 13,
          scrollBeyondLastLine: false,
          renderWhitespace: "none",
          // Without this, Monaco measures its container once at construction
          // time and never re-checks - if that first measurement lands
          // before the surrounding flex layout settles (common in a
          // responsive layout), the editor freezes at a near-zero size.
          automaticLayout: true,
        }}
      />
    </div>
  );
}
