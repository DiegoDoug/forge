"use client";

import { useMemo, useState } from "react";

import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";

export function RegexTool() {
  const [pattern, setPattern] = useState("\\b\\w+@\\w+\\.\\w+\\b");
  const [flags, setFlags] = useState("g");
  const [text, setText] = useState("Contact: forge@example.com or admin@forge.dev");

  const { matches, error, highlighted } = useMemo(() => {
    try {
      const re = new RegExp(pattern, flags.includes("g") ? flags : `${flags}g`);
      const found: RegExpExecArray[] = [];
      let m: RegExpExecArray | null;
      let guard = 0;
      while ((m = re.exec(text)) !== null && guard < 1000) {
        found.push(m);
        guard++;
        if (m[0] === "") re.lastIndex++;
      }

      const parts: { text: string; match: boolean }[] = [];
      let cursor = 0;
      for (const match of found) {
        if (match.index > cursor) parts.push({ text: text.slice(cursor, match.index), match: false });
        parts.push({ text: match[0], match: true });
        cursor = match.index + match[0].length;
      }
      if (cursor < text.length) parts.push({ text: text.slice(cursor), match: false });

      return { matches: found, error: null, highlighted: parts };
    } catch (err) {
      return { matches: [], error: err instanceof Error ? err.message : "Invalid regex", highlighted: [] };
    }
  }, [pattern, flags, text]);

  return (
    <ToolCard title="Regex tester" description="Live match highlighting and capture groups">
      <div className="flex items-center gap-2">
        <span className="font-mono text-muted-foreground">/</span>
        <Input value={pattern} onChange={(e) => setPattern(e.target.value)} className="flex-1 font-mono text-xs" />
        <span className="font-mono text-muted-foreground">/</span>
        <Input value={flags} onChange={(e) => setFlags(e.target.value)} className="w-16 font-mono text-xs" />
      </div>
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={3} className="font-mono text-xs" />

      {error ? (
        <p className="text-xs text-destructive">{error}</p>
      ) : (
        <>
          <div className="rounded-lg border border-border bg-muted/40 p-2 font-mono text-xs whitespace-pre-wrap">
            {highlighted.map((part, i) =>
              part.match ? (
                <mark key={i} className="rounded bg-primary/30 px-0.5 text-foreground">
                  {part.text}
                </mark>
              ) : (
                <span key={i}>{part.text}</span>
              ),
            )}
          </div>
          <p className="text-xs text-muted-foreground">{matches.length} match{matches.length === 1 ? "" : "es"}</p>
        </>
      )}
    </ToolCard>
  );
}
