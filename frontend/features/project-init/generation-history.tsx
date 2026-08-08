"use client";

import { useState } from "react";
import { Download, FolderClock, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { DataList, DataListRow, DataListSkeleton } from "@/components/data-list";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { formatRelativeTime } from "@/lib/format";
import { downloadGeneration, useProjectInitHistory, useProjectInitMutations, type GenerationListItem, type TemplateKind } from "./api";

const KIND_LABELS: Record<TemplateKind, string> = {
  fdk_phase: "FDK Phase",
  ai_instructions: "AI Instructions",
};

export function GenerationHistory() {
  const { data, isLoading, isError, refetch } = useProjectInitHistory();
  const { remove } = useProjectInitMutations();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<GenerationListItem | null>(null);

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

  function handleDelete() {
    if (!deleteTarget) return;
    remove.mutate(deleteTarget.id, { onError: () => toast.error("Couldn't delete that generation.") });
    setDeleteTarget(null);
  }

  if (isLoading) {
    return <DataListSkeleton rows={3} />;
  }

  if (isError) {
    return <ErrorState description="Couldn't load your generation history." onRetry={() => refetch()} />;
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
    <>
      <DataList>
        {items.map((item) => (
          <DataListRow key={item.id}>
            <Badge variant="secondary" className="shrink-0">
              {KIND_LABELS[item.kind]}
            </Badge>
            <div className="min-w-0 flex-1">
              <p className="data-primary truncate">{item.name}</p>
              <p className="data-meta">{formatRelativeTime(item.created_at)}</p>
            </div>
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
            <Button size="icon" variant="ghost" aria-label={`Delete ${item.name}`} onClick={() => setDeleteTarget(item)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </DataListRow>
        ))}
      </DataList>
      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete this generation?"
        description={`This removes "${deleteTarget?.name}" from your history. It doesn't affect any file you already downloaded.`}
        onConfirm={handleDelete}
      />
    </>
  );
}
