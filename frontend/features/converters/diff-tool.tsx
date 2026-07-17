"use client";

import { diffLines } from "diff";
import { useMemo, useState } from "react";

import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";

export function DiffTool() {
  const [left, setLeft] = useState("line one\nline two\nline three");
  const [right, setRight] = useState("line one\nline TWO\nline three\nline four");

  const changes = useMemo(() => diffLines(left, right), [left, right]);

  return (
    <ToolCard title="Diff viewer" description="Line-by-line comparison" className="md:col-span-2">
      <div className="grid grid-cols-2 gap-2">
        <Textarea value={left} onChange={(e) => setLeft(e.target.value)} rows={6} className="font-mono text-xs" />
        <Textarea value={right} onChange={(e) => setRight(e.target.value)} rows={6} className="font-mono text-xs" />
      </div>
      <pre className="max-h-64 overflow-auto rounded-lg border border-border bg-muted/40 p-2 font-mono text-xs whitespace-pre-wrap">
        {changes.map((part, i) => (
          <div
            key={i}
            className={
              part.added
                ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
                : part.removed
                  ? "bg-destructive/15 text-destructive"
                  : ""
            }
          >
            {part.value
              .split("\n")
              .filter((_, idx, arr) => idx < arr.length - 1 || arr.length === 1)
              .map((line, li) => (
                <div key={li}>
                  {part.added ? "+ " : part.removed ? "- " : "  "}
                  {line}
                </div>
              ))}
          </div>
        ))}
      </pre>
    </ToolCard>
  );
}
