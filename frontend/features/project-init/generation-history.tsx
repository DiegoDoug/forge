"use client";

import { useState } from "react";
import { Download, FolderClock, Loader2, Trash2 } from "lucide-react";
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
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/empty-state";
import { formatRelativeTime } from "@/lib/format";
import { downloadGeneration, useProjectInitHistory, useProjectInitMutations, type GenerationListItem, type TemplateKind } from "./api";

const KIND_LABELS: Record<TemplateKind, string> = {
  fdk_phase: "FDK Phase",
  ai_instructions: "AI Instructions",
};

export function GenerationHistory() {
  const { data, isLoading, isError } = useProjectInitHistory();
  const { remove } = useProjectInitMutations();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  async function handleDownload(item: GenerationListItem) {
    setDownloadingId(item.id);
    try {
      await downloadGeneration(item.id, item.name);
    } catch {
      toast.error("Couldn't download that generation.");
    } finally {
      setDownloadingId(null);
    }
  }

  function handleDelete(id: string) {
    remove.mutate(id, { onError: () => toast.error("Couldn't delete that generation.") });
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (isError) {
    return <p className="text-sm text-destructive">Couldn&apos;t load your generation history. Try reloading the page.</p>;
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return (
      <EmptyState
        icon={FolderClock}
        title="No generations yet"
        description="Use the form above to generate your first scaffold or instruction set."
      />
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {items.map((item) => (
        <li key={item.id} className="flex items-center justify-between gap-3 rounded-lg border border-border p-3">
          <div className="flex min-w-0 items-center gap-3">
            <Badge variant="secondary" className="shrink-0">
              {KIND_LABELS[item.kind]}
            </Badge>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{item.name}</p>
              <p className="text-xs text-muted-foreground">{formatRelativeTime(item.created_at)}</p>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <Button
              size="icon"
              variant="ghost"
              aria-label={`Download ${item.name}`}
              onClick={() => handleDownload(item)}
              disabled={downloadingId === item.id}
            >
              {downloadingId === item.id ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
            </Button>
            <AlertDialog>
              <AlertDialogTrigger render={<Button size="icon" variant="ghost" aria-label={`Delete ${item.name}`} />}>
                <Trash2 className="h-4 w-4" />
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete this generation?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This removes &quot;{item.name}&quot; from your history. It doesn&apos;t affect any file you
                    already downloaded.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleDelete(item.id)}>Delete</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </li>
      ))}
    </ul>
  );
}
