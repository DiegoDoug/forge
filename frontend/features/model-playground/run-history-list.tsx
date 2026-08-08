"use client";

import { useState } from "react";
import { History, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { DataList, DataListRow, DataListSkeleton } from "@/components/data-list";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { formatRelativeTime } from "@/lib/format";
import { useRunMutations, useRuns } from "./api";

export function RunHistoryList({
  activeRunId,
  onSelect,
}: {
  activeRunId: string | null;
  onSelect: (runId: string) => void;
}) {
  const runsQuery = useRuns();
  const { remove } = useRunMutations();
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await remove.mutateAsync(deleteTarget);
      toast.success("Run deleted");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete run");
    } finally {
      setDeleteTarget(null);
    }
  }

  if (runsQuery.isLoading) {
    return <DataListSkeleton rows={2} />;
  }

  if (runsQuery.isError) {
    return <ErrorState description="Couldn't load run history." onRetry={() => runsQuery.refetch()} />;
  }

  const runs = runsQuery.data?.items ?? [];

  if (runs.length === 0) {
    return <EmptyState icon={History} title="No runs yet" description="Comparisons you run will appear here." />;
  }

  return (
    <>
      <DataList>
        {runs.map((run) => (
          <DataListRow key={run.id} selected={activeRunId === run.id} className="items-start gap-2 py-2">
            <button
              type="button"
              className="flex min-w-0 flex-1 flex-col items-start gap-1 text-left"
              onClick={() => onSelect(run.id)}
            >
              <span className="data-primary truncate">{run.prompt_excerpt}</span>
              <div className="flex flex-wrap items-center gap-1">
                {run.providers.map((p) => (
                  <Badge key={p} variant="outline">
                    {p}
                  </Badge>
                ))}
                <span className="data-meta">{formatRelativeTime(run.created_at)}</span>
              </div>
            </button>
            <Button
              variant="ghost"
              size="icon-sm"
              className="shrink-0 text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                setDeleteTarget(run.id);
              }}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </DataListRow>
        ))}
      </DataList>
      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete this run?"
        description="This permanently deletes the prompt and its results. This cannot be undone."
        onConfirm={handleDelete}
      />
    </>
  );
}
