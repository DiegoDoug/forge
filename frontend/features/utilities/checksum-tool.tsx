"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { OutputField } from "@/components/output-field";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";

const ALGORITHMS: { label: string; value: "SHA-1" | "SHA-256" | "SHA-384" | "SHA-512" }[] = [
  { label: "SHA-1", value: "SHA-1" },
  { label: "SHA-256", value: "SHA-256" },
  { label: "SHA-384", value: "SHA-384" },
  { label: "SHA-512", value: "SHA-512" },
];

function toHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function ChecksumTool() {
  const [text, setText] = useState("");
  const [textHashes, setTextHashes] = useState<Record<string, string>>({});
  const [file, setFile] = useState<File | null>(null);
  const [fileHashes, setFileHashes] = useState<Record<string, string>>({});
  const [hashing, setHashing] = useState(false);

  async function hashText() {
    const encoded = new TextEncoder().encode(text);
    const results: Record<string, string> = {};
    for (const { value } of ALGORITHMS) {
      results[value] = toHex(await crypto.subtle.digest(value, encoded));
    }
    setTextHashes(results);
  }

  async function hashFile(f: File) {
    setFile(f);
    setHashing(true);
    try {
      const buffer = await f.arrayBuffer();
      const results: Record<string, string> = {};
      for (const { value } of ALGORITHMS) {
        results[value] = toHex(await crypto.subtle.digest(value, buffer));
      }
      setFileHashes(results);
    } finally {
      setHashing(false);
    }
  }

  return (
    <ToolCard title="Checksum & file hash" description="SHA-1/256/384/512, computed locally in your browser">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Text to hash…" rows={2} className="font-mono text-xs" />
      <Button size="sm" variant="outline" className="w-fit" onClick={hashText} disabled={!text}>
        Hash text
      </Button>
      {Object.keys(textHashes).length > 0 ? (
        <div className="flex flex-col gap-1">
          {ALGORITHMS.map((a) => (
            <OutputField key={a.value} value={textHashes[a.value] ?? ""} placeholder={a.label} />
          ))}
        </div>
      ) : null}

      <div className="mt-1 border-t border-border pt-3">
        <input
          type="file"
          onChange={(e) => e.target.files?.[0] && hashFile(e.target.files[0])}
          className="text-xs file:mr-2 file:rounded-md file:border-0 file:bg-secondary file:px-2 file:py-1 file:text-xs"
        />
        {file ? <p className="mt-1 text-xs text-muted-foreground">{file.name} · {(file.size / 1024).toFixed(1)} KB</p> : null}
        {hashing ? <p className="text-xs text-muted-foreground">Hashing…</p> : null}
        {Object.keys(fileHashes).length > 0 && !hashing ? (
          <div className="mt-1 flex flex-col gap-1">
            {ALGORITHMS.map((a) => (
              <OutputField key={a.value} value={fileHashes[a.value] ?? ""} placeholder={a.label} />
            ))}
          </div>
        ) : null}
      </div>
    </ToolCard>
  );
}
