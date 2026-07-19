"use client";

import { useState } from "react";
import Papa from "papaparse";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { CopyButton } from "@/components/copy-button";

export function CsvTool() {
  const [input, setInput] = useState("name,role\nAda,Engineer\nGrace,Engineer");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [headerRow, setHeaderRow] = useState(true);

  function toJson() {
    const result = Papa.parse<Record<string, string> | string[]>(input, {
      header: headerRow,
      skipEmptyLines: true,
    });
    if (result.errors.length) {
      setError(result.errors[0].message);
      setOutput("");
      return;
    }
    setOutput(JSON.stringify(result.data, null, 2));
    setError(null);
  }

  function toCsv() {
    try {
      const data = JSON.parse(input);
      if (!Array.isArray(data)) throw new Error("JSON must be an array of rows");
      setOutput(Papa.unparse(data, { header: headerRow }));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid JSON");
      setOutput("");
    }
  }

  return (
    <ToolCard title="CSV" description="Convert between CSV and JSON">
      <Textarea value={input} onChange={(e) => setInput(e.target.value)} rows={6} className="font-mono text-xs" />
      <label className="flex items-center gap-2 text-xs text-muted-foreground">
        <Checkbox checked={headerRow} onCheckedChange={(v) => setHeaderRow(Boolean(v))} />
        First row is a header
      </label>
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={toJson}>
          CSV → JSON
        </Button>
        <Button size="sm" variant="outline" onClick={toCsv}>
          JSON → CSV
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
