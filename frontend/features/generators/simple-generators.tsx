"use client";

import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { OutputField } from "@/components/output-field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ToolCard } from "@/components/tool-card";
import { generatorsApi } from "./api";

export function UuidGenerator() {
  const v4 = useMutation({ mutationFn: generatorsApi.uuid4 });
  const v7 = useMutation({ mutationFn: generatorsApi.uuid7 });

  useEffect(() => {
    v4.mutate();
    v7.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ToolCard title="UUID" description="v4 (random) and v7 (time-ordered)">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span className="w-10 shrink-0 text-xs text-muted-foreground">v4</span>
          <OutputField value={v4.data?.value ?? ""} className="flex-1" />
          <Button variant="ghost" size="icon-sm" onClick={() => v4.mutate()}>
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-10 shrink-0 text-xs text-muted-foreground">v7</span>
          <OutputField value={v7.data?.value ?? ""} className="flex-1" />
          <Button variant="ghost" size="icon-sm" onClick={() => v7.mutate()}>
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </ToolCard>
  );
}

export function NanoIdGenerator() {
  const [size, setSize] = useState(21);
  const generate = useMutation({ mutationFn: () => generatorsApi.nanoid({ size }) });

  useEffect(() => {
    generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ToolCard title="NanoID" description="Compact, URL-safe unique ID">
      <OutputField value={generate.data?.value ?? ""} />
      <div className="flex items-center gap-2">
        <Label className="text-xs text-muted-foreground">Size</Label>
        <Input
          type="number"
          value={size}
          onChange={(e) => setSize(Number(e.target.value))}
          className="h-7 w-20 text-xs"
          min={1}
          max={512}
        />
        <Button variant="outline" size="sm" onClick={() => generate.mutate()}>
          <RefreshCw className="h-3.5 w-3.5" />
          Regenerate
        </Button>
      </div>
    </ToolCard>
  );
}

export function RandomBytesGenerator() {
  const [length, setLength] = useState(32);
  const [encoding, setEncoding] = useState<"hex" | "base64" | "base64url">("hex");
  const generate = useMutation({ mutationFn: () => generatorsApi.randomBytes({ length, encoding }) });

  useEffect(() => {
    generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ToolCard title="Random bytes" description="Raw entropy for keys and salts">
      <OutputField value={generate.data?.value ?? ""} />
      <div className="flex items-center gap-2">
        <Input
          type="number"
          value={length}
          onChange={(e) => setLength(Number(e.target.value))}
          className="h-7 w-20 text-xs"
          min={1}
          max={4096}
        />
        <Select value={encoding} onValueChange={(v) => v && setEncoding(v as typeof encoding)}>
          <SelectTrigger className="h-7 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="hex">hex</SelectItem>
            <SelectItem value="base64">base64</SelectItem>
            <SelectItem value="base64url">base64url</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm" onClick={() => generate.mutate()}>
          <RefreshCw className="h-3.5 w-3.5" />
          Regenerate
        </Button>
      </div>
    </ToolCard>
  );
}

export function ApiKeyGenerator() {
  const [prefix, setPrefix] = useState("forge");
  const generate = useMutation({ mutationFn: () => generatorsApi.apiKey({ prefix }) });

  useEffect(() => {
    generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ToolCard title="API key" description="Prefixed, URL-safe token">
      <OutputField value={generate.data?.value ?? ""} />
      <div className="flex items-center gap-2">
        <Label className="text-xs text-muted-foreground">Prefix</Label>
        <Input value={prefix} onChange={(e) => setPrefix(e.target.value)} className="h-7 w-24 text-xs" />
        <Button variant="outline" size="sm" onClick={() => generate.mutate()}>
          <RefreshCw className="h-3.5 w-3.5" />
          Regenerate
        </Button>
      </div>
    </ToolCard>
  );
}

export function JwtSecretGenerator() {
  const [length, setLength] = useState(64);
  const generate = useMutation({ mutationFn: () => generatorsApi.jwtSecret({ length }) });

  useEffect(() => {
    generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ToolCard title="JWT / HMAC secret" description="Base64url signing secret">
      <OutputField value={generate.data?.value ?? ""} />
      <div className="flex items-center gap-2">
        <Input
          type="number"
          value={length}
          onChange={(e) => setLength(Number(e.target.value))}
          className="h-7 w-20 text-xs"
          min={16}
          max={512}
        />
        <Button variant="outline" size="sm" onClick={() => generate.mutate()}>
          <RefreshCw className="h-3.5 w-3.5" />
          Regenerate
        </Button>
      </div>
    </ToolCard>
  );
}
