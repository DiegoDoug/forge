"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { CopyButton } from "@/components/copy-button";

export function JsonTool() {
  const [input, setInput] = useState('{\n  "hello": "world"\n}');
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);

  function run(indent: number | null) {
    try {
      const parsed = JSON.parse(input);
      setOutput(indent === null ? JSON.stringify(parsed) : JSON.stringify(parsed, null, indent));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid JSON");
      setOutput("");
    }
  }

  return (
    <ToolCard title="JSON" description="Format, minify, and validate">
      <Textarea value={input} onChange={(e) => setInput(e.target.value)} rows={6} className="font-mono text-xs" />
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={() => run(2)}>
          Format
        </Button>
        <Button size="sm" variant="outline" onClick={() => run(null)}>
          Minify
        </Button>
      </div>
      {error ? (
        <p className="text-xs text-destructive">{error}</p>
      ) : output ? (
        <div className="relative">
          <pre className="max-h-64 overflow-auto rounded-lg border border-border bg-muted/40 p-3 pr-10 font-mono text-xs whitespace-pre-wrap">
            {output}
          </pre>
          <CopyButton value={output} className="absolute top-1.5 right-1.5" />
        </div>
      ) : null}
    </ToolCard>
  );
}
