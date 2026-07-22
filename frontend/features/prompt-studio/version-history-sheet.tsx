"use client";

import { useState } from "react";
import { diffLines } from "diff";
import { History } from "lucide-react";
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
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelativeTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { usePromptStudioMutations, usePromptVersion, usePromptVersions } from "./api";

export function VersionHistorySheet({
  promptId,
  open,
  onOpenChange,
}: {
  promptId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [selected, setSelected] = useState<string[]>([]);
  const { data, isLoading, isError } = usePromptVersions(open ? promptId : null);
  const { restoreVersion } = usePromptStudioMutations();

  const versions = data?.items ?? [];

  function toggleSelect(id: string) {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((v) => v !== id);
      if (prev.length >= 2) return [prev[1], id];
      return [...prev, id];
    });
  }

  function handleRestore(versionId: string) {
    restoreVersion.mutate(
      { id: promptId, versionId },
      {
        onSuccess: () => toast.success("Restored version."),
        onError: () => toast.error("Couldn't restore that version."),
      },
    );
  }

  return (
    <Sheet
      open={open}
      onOpenChange={(next) => {
        onOpenChange(next);
        if (!next) setSelected([]);
      }}
    >
      <SheetContent className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Version history</SheetTitle>
        </SheetHeader>
        <ScrollArea className="min-h-0 flex-1 px-4">
          {isLoading ? (
            <div className="flex flex-col gap-2 pb-4">
              {[0, 1, 2].map((i) => (
                <Skeleton key={i} className="h-12 w-full rounded-lg" />
              ))}
            </div>
          ) : isError ? (
            <p className="text-sm text-destructive">Couldn&apos;t load version history.</p>
          ) : versions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No versions yet.</p>
          ) : (
            <div className="flex flex-col gap-1 pb-4">
              {versions.map((version) => (
                <button
                  key={version.id}
                  onClick={() => toggleSelect(version.id)}
                  className={cn(
                    "flex items-center justify-between gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                    selected.includes(version.id) ? "border-foreground bg-muted/50" : "border-border hover:bg-accent/50",
                  )}
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">v{version.version_number}</Badge>
                      <span className="truncate text-xs text-muted-foreground">{version.note}</span>
                    </div>
                    <span className="text-[11px] text-muted-foreground">{formatRelativeTime(version.created_at)}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </ScrollArea>

        {selected.length === 2 ? (
          <VersionDiff promptId={promptId} versionIds={selected} />
        ) : selected.length === 1 ? (
          <VersionDetail promptId={promptId} versionId={selected[0]} onRestore={handleRestore} />
        ) : (
          <p className="px-4 pb-4 text-xs text-muted-foreground">
            Select one version to view or restore it, or two to see a diff.
          </p>
        )}
      </SheetContent>
    </Sheet>
  );
}

function VersionDetail({
  promptId,
  versionId,
  onRestore,
}: {
  promptId: string;
  versionId: string;
  onRestore: (versionId: string) => void;
}) {
  const { data: version, isLoading } = usePromptVersion(promptId, versionId);

  if (isLoading || !version) {
    return <Skeleton className="mx-4 mb-4 h-32 rounded-lg" />;
  }

  return (
    <div className="flex flex-col gap-2 border-t border-border p-4">
      <pre className="max-h-40 overflow-auto rounded-lg border border-border bg-muted/40 p-2 font-mono text-xs whitespace-pre-wrap">
        {version.body}
      </pre>
      <AlertDialog>
        <AlertDialogTrigger render={<Button size="sm" variant="outline" />}>
          <History className="h-3.5 w-3.5" />
          Restore this version
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Restore v{version.version_number}?</AlertDialogTitle>
            <AlertDialogDescription>
              This makes v{version.version_number}&apos;s content the prompt&apos;s current content again. Nothing is
              lost — this creates a new version rather than deleting any history.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => onRestore(versionId)}>Restore</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

function VersionDiff({ promptId, versionIds }: { promptId: string; versionIds: string[] }) {
  const a = usePromptVersion(promptId, versionIds[0]);
  const b = usePromptVersion(promptId, versionIds[1]);

  if (a.isLoading || b.isLoading || !a.data || !b.data) {
    return <Skeleton className="mx-4 mb-4 h-32 rounded-lg" />;
  }

  // Diff oldest -> newest, regardless of click order.
  const [older, newer] = a.data.version_number <= b.data.version_number ? [a.data, b.data] : [b.data, a.data];
  const changes = diffLines(older.body, newer.body);

  return (
    <div className="flex flex-col gap-2 border-t border-border p-4">
      <p className="text-xs text-muted-foreground">
        Diffing v{older.version_number} → v{newer.version_number}
      </p>
      <pre className="max-h-56 overflow-auto rounded-lg border border-border bg-muted/40 p-2 font-mono text-xs whitespace-pre-wrap">
        {changes.map((part, i) => (
          <div
            key={i}
            className={
              part.added
                ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
                : part.removed
                  ? "bg-destructive/15 text-destructive"
                  : ""
            }
          >
            {part.value
              .split("\n")
              .filter((_, idx, arr) => idx < arr.length - 1 || arr.length === 1)
              .map((line, li) => (
                <div key={li}>
                  {part.added ? "+ " : part.removed ? "- " : "  "}
                  {line}
                </div>
              ))}
          </div>
        ))}
      </pre>
    </div>
  );
}
