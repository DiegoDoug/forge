"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { formatRelativeTime } from "@/lib/format";
import { ResultPanel } from "@/features/model-playground/result-panel";
import type { PlaygroundRun } from "@/features/model-playground/api";
import type { Project } from "./api";
import { useProjectAiRun, useProjectAiRuns } from "./api";

export function ProjectAiQuickRun({ project }: { project: Project }) {
  const [prompt, setPrompt] = useState("");
  const [lastRun, setLastRun] = useState<PlaygroundRun | null>(null);
  const runMutation = useProjectAiRun(project.id);
  const runsQuery = useProjectAiRuns(project.id);

  const ready = Boolean(project.default_provider && project.default_model);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!prompt.trim() || !ready) return;
    try {
      const run = await runMutation.mutateAsync(prompt.trim());
      setLastRun(run);
      setPrompt("");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "AI run failed");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Run a prompt</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <Textarea
            placeholder={ready ? "Ask something in this project's context…" : "Set a default AI provider first"}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={!ready}
            className="min-h-20"
          />
          <div className="flex justify-end">
            <Button type="submit" size="sm" disabled={!ready || !prompt.trim() || runMutation.isPending}>
              <Send className="h-3.5 w-3.5" />
              {runMutation.isPending ? "Running…" : "Run"}
            </Button>
          </div>
        </form>

        {lastRun ? (
          <div className="flex flex-col gap-1">
            {lastRun.results.map((result) => (
              <ResultPanel key={result.id} result={result} />
            ))}
          </div>
        ) : null}

        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-muted-foreground">Recent activity</span>
          {runsQuery.isLoading ? (
            <Skeleton className="h-8 w-full" />
          ) : (runsQuery.data?.items.length ?? 0) === 0 ? (
            <p className="text-xs text-muted-foreground">No AI runs in this project yet.</p>
          ) : (
            <ul className="flex flex-col gap-1">
              {runsQuery.data!.items.map((item) => (
                <li key={item.id} className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
                  <span className="truncate">{item.prompt_excerpt}</span>
                  <span className="shrink-0">{formatRelativeTime(item.created_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
