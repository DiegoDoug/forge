"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { OutputField } from "@/components/output-field";
import { ToolCard } from "@/components/tool-card";

export function TimestampTool() {
  const [epoch, setEpoch] = useState(() => Math.floor(Date.now() / 1000).toString());
  const [iso, setIso] = useState(() => new Date().toISOString());

  function fromEpoch(value: string) {
    setEpoch(value);
    const n = Number(value);
    if (!Number.isNaN(n)) {
      const ms = value.length > 10 ? n : n * 1000;
      const d = new Date(ms);
      if (!Number.isNaN(d.getTime())) setIso(d.toISOString());
    }
  }

  function fromIso(value: string) {
    setIso(value);
    const d = new Date(value);
    if (!Number.isNaN(d.getTime())) setEpoch(Math.floor(d.getTime() / 1000).toString());
  }

  function now() {
    const d = new Date();
    setEpoch(Math.floor(d.getTime() / 1000).toString());
    setIso(d.toISOString());
  }

  const date = new Date(iso);
  const local = Number.isNaN(date.getTime())
    ? ""
    : date.toLocaleString(undefined, { dateStyle: "full", timeStyle: "long" });

  return (
    <ToolCard title="Timestamp converter" description="Unix epoch, ISO 8601, and local time">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span className="w-16 shrink-0 text-xs text-muted-foreground">Epoch</span>
          <Input value={epoch} onChange={(e) => fromEpoch(e.target.value)} className="font-mono text-xs" />
        </div>
        <div className="flex items-center gap-2">
          <span className="w-16 shrink-0 text-xs text-muted-foreground">ISO 8601</span>
          <Input value={iso} onChange={(e) => fromIso(e.target.value)} className="font-mono text-xs" />
        </div>
        <Button size="sm" variant="outline" className="w-fit" onClick={now}>
          Now
        </Button>
        <OutputField value={local} placeholder="Local time" mono={false} />
      </div>
    </ToolCard>
  );
}
