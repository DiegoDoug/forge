"use client";

import { useState } from "react";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { CopyButton } from "@/components/copy-button";

export function YamlTool() {
  const [input, setInput] = useState("hello: world\nlist:\n  - one\n  - two\n");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);

  function toJson() {
    try {
      setOutput(JSON.stringify(parseYaml(input), null, 2));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid YAML");
      setOutput("");
    }
  }

  function toYaml() {
    try {
      setOutput(stringifyYaml(JSON.parse(input)));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid JSON");
      setOutput("");
    }
  }

  return (
    <ToolCard title="YAML" description="Convert between YAML and JSON">
      <Textarea value={input} onChange={(e) => setInput(e.target.value)} rows={6} className="font-mono text-xs" />
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={toJson}>
          YAML → JSON
        </Button>
        <Button size="sm" variant="outline" onClick={toYaml}>
          JSON → YAML
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
