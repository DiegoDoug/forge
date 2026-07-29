"use client";

import { History, Trash2 } from "lucide-react";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
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

  async function handleDelete(runId: string) {
    try {
      await remove.mutateAsync(runId);
      toast.success("Run deleted");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete run");
    }
  }

  if (runsQuery.isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    );
  }

  const runs = runsQuery.data?.items ?? [];

  if (runs.length === 0) {
    return <EmptyState icon={History} title="No runs yet" description="Comparisons you run will appear here." />;
  }

  return (
    <div className="flex flex-col gap-2">
      {runs.map((run) => (
        <div
          key={run.id}
          className={cn(
            "flex items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-sm transition-colors hover:bg-muted/50",
            activeRunId === run.id && "border-ring bg-muted/50",
          )}
        >
          <button type="button" className="flex min-w-0 flex-1 flex-col items-start gap-1 text-left" onClick={() => onSelect(run.id)}>
            <span className="truncate">{run.prompt_excerpt}</span>
            <div className="flex flex-wrap items-center gap-1">
              {run.providers.map((p) => (
                <Badge key={p} variant="outline">
                  {p}
                </Badge>
              ))}
              <span className="text-xs text-muted-foreground">{formatRelativeTime(run.created_at)}</span>
            </div>
          </button>
          <AlertDialog>
            <AlertDialogTrigger render={<Button variant="ghost" size="icon-sm" className="shrink-0 text-destructive" />}>
              <Trash2 className="h-3.5 w-3.5" />
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this run?</AlertDialogTitle>
                <AlertDialogDescription>This permanently deletes the prompt and its results. This cannot be undone.</AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  className="bg-destructive text-white hover:bg-destructive/90"
                  onClick={() => handleDelete(run.id)}
                >
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      ))}
    </div>
  );
}
