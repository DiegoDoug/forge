"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { OutputField } from "@/components/output-field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { cryptoApi } from "./api";

const ALGORITHMS = ["HS256", "HS384", "HS512"];

export function JwtDecodeTool() {
  const [token, setToken] = useState("");
  const decode = useMutation({
    mutationFn: () => cryptoApi.jwtDecode(token),
    onError: (err) => toast.error(err instanceof Error ? err.message : "Invalid JWT"),
  });

  return (
    <ToolCard title="Decode" description="Inspect a JWT's header and payload (no signature check)">
      <Textarea value={token} onChange={(e) => setToken(e.target.value)} placeholder="eyJhbGciOi…" rows={3} className="font-mono text-xs" />
      <Button size="sm" variant="outline" className="w-fit" onClick={() => decode.mutate()} disabled={!token}>
        Decode
      </Button>
      {decode.data ? (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Header</p>
            <pre className="max-h-40 overflow-auto rounded-lg border border-border bg-muted/40 p-2 text-xs">
              {JSON.stringify(decode.data.header, null, 2)}
            </pre>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Payload</p>
            <pre className="max-h-40 overflow-auto rounded-lg border border-border bg-muted/40 p-2 text-xs">
              {JSON.stringify(decode.data.payload, null, 2)}
            </pre>
          </div>
        </div>
      ) : null}
    </ToolCard>
  );
}

export function JwtVerifyTool() {
  const [token, setToken] = useState("");
  const [secret, setSecret] = useState("");
  const [algorithm, setAlgorithm] = useState("HS256");
  const verify = useMutation({ mutationFn: () => cryptoApi.jwtVerify(token, secret, algorithm) });

  return (
    <ToolCard title="Verify" description="Check a JWT's signature against a secret">
      <Textarea value={token} onChange={(e) => setToken(e.target.value)} placeholder="eyJhbGciOi…" rows={3} className="font-mono text-xs" />
      <div className="flex items-center gap-2">
        <Input value={secret} onChange={(e) => setSecret(e.target.value)} placeholder="Secret" className="h-8 flex-1" />
        <Select value={algorithm} onValueChange={(v) => v && setAlgorithm(v)}>
          <SelectTrigger className="h-8 w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ALGORITHMS.map((a) => (
              <SelectItem key={a} value={a}>
                {a}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button size="sm" variant="outline" onClick={() => verify.mutate()} disabled={!token || !secret}>
          Verify
        </Button>
      </div>
      {verify.data ? (
        <p className={`text-xs font-medium ${verify.data.valid ? "text-emerald-500" : "text-destructive"}`}>
          {verify.data.valid ? "Valid signature" : `Invalid: ${verify.data.error}`}
        </p>
      ) : null}
    </ToolCard>
  );
}

export function JwtBuildTool() {
  const [payload, setPayload] = useState('{\n  "sub": "user-id"\n}');
  const [secret, setSecret] = useState("");
  const [algorithm, setAlgorithm] = useState("HS256");
  const [expiresIn, setExpiresIn] = useState(3600);

  const build = useMutation({
    mutationFn: () => {
      let parsed: Record<string, unknown>;
      try {
        parsed = JSON.parse(payload);
      } catch {
        throw new Error("Payload must be valid JSON");
      }
      return cryptoApi.jwtBuild(parsed, secret, algorithm, expiresIn || undefined);
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to build JWT"),
  });

  return (
    <ToolCard title="Build" description="Sign a new JWT">
      <Textarea value={payload} onChange={(e) => setPayload(e.target.value)} rows={4} className="font-mono text-xs" />
      <div className="flex items-center gap-2">
        <Input value={secret} onChange={(e) => setSecret(e.target.value)} placeholder="Secret" className="h-8 flex-1" />
        <Select value={algorithm} onValueChange={(v) => v && setAlgorithm(v)}>
          <SelectTrigger className="h-8 w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ALGORITHMS.map((a) => (
              <SelectItem key={a} value={a}>
                {a}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center gap-2">
        <Input
          type="number"
          value={expiresIn}
          onChange={(e) => setExpiresIn(Number(e.target.value))}
          placeholder="Expires in (seconds)"
          className="h-8 w-40"
        />
        <Button size="sm" variant="outline" onClick={() => build.mutate()} disabled={!secret}>
          Sign
        </Button>
      </div>
      {build.data ? <OutputField value={build.data.text} /> : null}
    </ToolCard>
  );
}
