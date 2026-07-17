"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { OutputField } from "@/components/output-field";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";

export function UrlEncodeTool() {
  const [text, setText] = useState("");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);

  function encode() {
    setError(null);
    setOutput(encodeURIComponent(text));
  }
  function decode() {
    try {
      setOutput(decodeURIComponent(text));
      setError(null);
    } catch {
      setError("Invalid percent-encoded input");
    }
  }

  return (
    <ToolCard title="URL encode / decode" description="Percent-encode text for use in a URL">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} className="font-mono text-xs" />
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={encode} disabled={!text}>
          Encode
        </Button>
        <Button size="sm" variant="outline" onClick={decode} disabled={!text}>
          Decode
        </Button>
      </div>
      {error ? <p className="text-xs text-destructive">{error}</p> : <OutputField value={output} />}
    </ToolCard>
  );
}

export function UnicodeInspector() {
  const [text, setText] = useState("café 👋");

  const chars = Array.from(text).map((ch) => ({
    ch,
    codepoint: `U+${ch.codePointAt(0)!.toString(16).toUpperCase().padStart(4, "0")}`,
  }));
  const escaped = Array.from(text)
    .map((ch) => `\\u{${ch.codePointAt(0)!.toString(16)}}`)
    .join("");

  return (
    <ToolCard title="Unicode inspector" description="Code points and JS escape sequence for each character">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} className="font-mono text-xs" />
      <div className="flex max-h-32 flex-wrap gap-1.5 overflow-auto">
        {chars.map((c, i) => (
          <div key={i} className="flex flex-col items-center gap-0.5 rounded-md border border-border px-2 py-1 text-xs">
            <span className="font-mono">{c.ch}</span>
            <span className="text-[10px] text-muted-foreground">{c.codepoint}</span>
          </div>
        ))}
      </div>
      <OutputField value={escaped} placeholder="Escaped output" />
    </ToolCard>
  );
}
