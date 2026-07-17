"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ToolCard } from "@/components/tool-card";

interface CronParseOut {
  description: string;
  next_runs: string[];
}

export function CronTool() {
  const [expression, setExpression] = useState("*/15 * * * *");

  const parse = useMutation({
    mutationFn: () => api.post<CronParseOut>("/api/converters/cron/parse", { expression, count: 5 }),
  });

  return (
    <ToolCard title="Cron parser" description="Explain a cron expression and preview upcoming runs (UTC)">
      <div className="flex items-center gap-2">
        <Input value={expression} onChange={(e) => setExpression(e.target.value)} className="font-mono text-xs" />
        <Button size="sm" variant="outline" onClick={() => parse.mutate()} disabled={!expression}>
          Parse
        </Button>
      </div>
      {parse.isError ? (
        <p className="text-xs text-destructive">{parse.error instanceof Error ? parse.error.message : "Invalid expression"}</p>
      ) : parse.data ? (
        <div className="flex flex-col gap-1.5">
          <p className="text-xs text-muted-foreground">{parse.data.description}</p>
          <ul className="flex flex-col gap-1 text-xs">
            {parse.data.next_runs.map((run) => (
              <li key={run} className="rounded-md border border-border bg-muted/40 px-2 py-1 font-mono">
                {run}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </ToolCard>
  );
}
