"use client";

import { FlaskConical } from "lucide-react";
import { toast } from "sonner";

import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useRun, useRunMutations, type RunTarget } from "./api";
import { PromptComposer } from "./prompt-composer";
import { ResultPanel } from "./result-panel";

export function RunView({
  activeRunId,
  onRunCreated,
}: {
  activeRunId: string | null;
  onRunCreated: (runId: string) => void;
}) {
  const runQuery = useRun(activeRunId);
  const { create } = useRunMutations();

  async function handleSubmit(prompt: string, targets: RunTarget[]) {
    try {
      const run = await create.mutateAsync({ prompt, targets });
      onRunCreated(run.id);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to start the comparison");
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <PromptComposer onSubmit={handleSubmit} isSubmitting={create.isPending} />

      {create.isPending ? (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      ) : activeRunId && runQuery.isLoading ? (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-40 w-full" />
        </div>
      ) : activeRunId && runQuery.data ? (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {runQuery.data.results.map((result) => (
            <ResultPanel key={result.id} result={result} />
          ))}
        </div>
      ) : activeRunId && runQuery.isError ? (
        <EmptyState
          icon={FlaskConical}
          title="Couldn't load this run"
          description="It may have been deleted. Pick another one from history, or run a new comparison."
        />
      ) : (
        <EmptyState
          icon={FlaskConical}
          title="No comparison yet"
          description="Write a prompt above and select one or more provider/model combinations to compare their responses."
        />
      )}
    </div>
  );
}
