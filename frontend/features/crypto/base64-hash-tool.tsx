"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { OutputField } from "@/components/output-field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { cryptoApi } from "./api";

const HASH_ALGORITHMS = ["md5", "sha1", "sha256", "sha384", "sha512", "blake2b", "blake2s"];

export function Base64Tool() {
  const [text, setText] = useState("");
  const [urlSafe, setUrlSafe] = useState(false);

  const encode = useMutation({ mutationFn: () => cryptoApi.base64Encode(text, urlSafe) });
  const decode = useMutation({ mutationFn: () => cryptoApi.base64Decode(text, urlSafe) });

  return (
    <ToolCard title="Base64" description="Encode or decode text">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Text or base64…" rows={3} className="font-mono text-xs" />
      <label className="flex items-center gap-2 text-xs text-muted-foreground">
        <Checkbox checked={urlSafe} onCheckedChange={(v) => setUrlSafe(Boolean(v))} />
        URL-safe alphabet
      </label>
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={() => encode.mutate()} disabled={!text}>
          Encode
        </Button>
        <Button size="sm" variant="outline" onClick={() => decode.mutate()} disabled={!text}>
          Decode
        </Button>
      </div>
      <OutputField value={encode.data?.text ?? decode.data?.text ?? ""} />
    </ToolCard>
  );
}

export function HashTool() {
  const [text, setText] = useState("");
  const [algorithm, setAlgorithm] = useState("sha256");
  const [expected, setExpected] = useState("");

  const hash = useMutation({ mutationFn: () => cryptoApi.hash(text, algorithm) });
  const verify = useMutation({ mutationFn: () => cryptoApi.verifyHash(text, algorithm, expected) });

  return (
    <ToolCard title="Hash" description="Digest and verify text against a known hash">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Text to hash…" rows={2} className="font-mono text-xs" />
      <Select value={algorithm} onValueChange={(v) => v && setAlgorithm(v)}>
        <SelectTrigger className="w-full">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {HASH_ALGORITHMS.map((a) => (
            <SelectItem key={a} value={a}>
              {a}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button size="sm" variant="outline" onClick={() => hash.mutate()} disabled={!text}>
        Compute hash
      </Button>
      <OutputField value={hash.data?.digest ?? ""} />

      <div className="mt-1 flex items-center gap-2">
        <input
          value={expected}
          onChange={(e) => setExpected(e.target.value)}
          placeholder="Compare against a hash…"
          className="h-8 flex-1 rounded-lg border border-input bg-transparent px-2.5 text-xs outline-none focus-visible:border-ring"
        />
        <Button size="sm" variant="outline" onClick={() => verify.mutate()} disabled={!text || !expected}>
          Verify
        </Button>
      </div>
      {verify.data ? (
        <p className={`text-xs font-medium ${verify.data.valid ? "text-emerald-500" : "text-destructive"}`}>
          {verify.data.valid ? "Match" : "Does not match"}
        </p>
      ) : null}
    </ToolCard>
  );
}
