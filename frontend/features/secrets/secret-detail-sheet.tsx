"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Eye, EyeOff, History, Pencil, Trash2 } from "lucide-react";
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
import { CopyButton } from "@/components/copy-button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { formatRelativeTime } from "@/lib/format";
import { secretsApi, useSecretsMutations } from "./api";
import { SECRET_TYPE_LABELS } from "./secret-types";

export function SecretDetailSheet({
  secretId,
  onClose,
  onEdit,
}: {
  secretId: string | null;
  onClose: () => void;
  onEdit: () => void;
}) {
  const [revealed, setRevealed] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const { deleteSecret } = useSecretsMutations();

  const detailQuery = useQuery({
    queryKey: ["secrets", "secret", secretId, revealed],
    queryFn: () => secretsApi.getSecret(secretId as string, revealed),
    enabled: Boolean(secretId),
  });

  const versionsQuery = useQuery({
    queryKey: ["secrets", "secret", secretId, "versions"],
    queryFn: () => secretsApi.listVersions(secretId as string),
    enabled: Boolean(secretId) && showVersions,
  });

  function handleClose(open: boolean) {
    if (!open) {
      setRevealed(false);
      setShowVersions(false);
      onClose();
    }
  }

  async function handleDelete() {
    if (!secretId) return;
    try {
      await deleteSecret.mutateAsync(secretId);
      toast.success("Secret deleted");
      onClose();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete secret");
    }
  }

  const secret = detailQuery.data;

  return (
    <Sheet open={Boolean(secretId)} onOpenChange={handleClose}>
      <SheetContent side="right" className="w-full sm:max-w-md">
        {secret ? (
          <>
            <SheetHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <SheetTitle>{secret.name}</SheetTitle>
                  <Badge variant="secondary" className="mt-1">
                    {SECRET_TYPE_LABELS[secret.type]}
                  </Badge>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon-sm" onClick={onEdit}>
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <AlertDialog>
                    <AlertDialogTrigger render={<Button variant="ghost" size="icon-sm" className="text-destructive" />}>
                      <Trash2 className="h-3.5 w-3.5" />
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete “{secret.name}”?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This permanently deletes the secret and its version history. This cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          className="bg-destructive text-white hover:bg-destructive/90"
                          onClick={handleDelete}
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </SheetHeader>

            <ScrollArea className="flex-1 px-4">
              <div className="flex flex-col gap-4 pb-6">
                <div className="flex flex-col gap-1.5">
                  <span className="text-xs font-medium text-muted-foreground">Value</span>
                  <div className="flex items-center gap-1 rounded-lg border border-border bg-muted/40 px-3 py-2">
                    <code className="flex-1 truncate font-mono text-sm">
                      {revealed && secret.value ? secret.value : "••••••••••••••••"}
                    </code>
                    <Button variant="ghost" size="icon-sm" onClick={() => setRevealed((r) => !r)}>
                      {revealed ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                    </Button>
                    {revealed && secret.value ? <CopyButton value={secret.value} label="Value copied" /> : null}
                  </div>
                </div>

                {secret.metadata.username ? (
                  <Field label="Username" value={secret.metadata.username} />
                ) : null}
                {secret.metadata.url ? <Field label="URL" value={secret.metadata.url} /> : null}
                {secret.metadata.notes ? (
                  <div className="flex flex-col gap-1.5">
                    <span className="text-xs font-medium text-muted-foreground">Notes</span>
                    <p className="rounded-lg border border-border bg-muted/40 px-3 py-2 text-sm whitespace-pre-wrap">
                      {secret.metadata.notes}
                    </p>
                  </div>
                ) : null}

                <Separator />

                <div className="flex flex-col gap-1 text-xs text-muted-foreground">
                  <span>Created {formatRelativeTime(secret.created_at)}</span>
                  <span>Updated {formatRelativeTime(secret.updated_at)}</span>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  className="w-fit"
                  onClick={() => setShowVersions((s) => !s)}
                >
                  <History className="h-3.5 w-3.5" />
                  Version history
                </Button>

                {showVersions ? (
                  <div className="flex flex-col gap-2">
                    {versionsQuery.isLoading ? (
                      <p className="text-xs text-muted-foreground">Loading…</p>
                    ) : versionsQuery.data && versionsQuery.data.length > 0 ? (
                      versionsQuery.data.map((v) => <VersionRow key={v.id} secretId={secret.id} versionId={v.id} createdAt={v.created_at} />)
                    ) : (
                      <p className="text-xs text-muted-foreground">No prior versions.</p>
                    )}
                  </div>
                ) : null}
              </div>
            </ScrollArea>
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">Loading…</div>
        )}
      </SheetContent>
    </Sheet>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <div className="flex items-center gap-1 rounded-lg border border-border bg-muted/40 px-3 py-2">
        <span className="flex-1 truncate text-sm">{value}</span>
        <CopyButton value={value} />
      </div>
    </div>
  );
}

function VersionRow({ secretId, versionId, createdAt }: { secretId: string; versionId: string; createdAt: string }) {
  const [revealed, setRevealed] = useState(false);
  const query = useQuery({
    queryKey: ["secrets", "secret", secretId, "versions", versionId],
    queryFn: () => secretsApi.revealVersion(secretId, versionId),
    enabled: revealed,
  });

  return (
    <div className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-xs">
      <span className="flex-1 text-muted-foreground">{formatRelativeTime(createdAt)}</span>
      {revealed && query.data ? (
        <>
          <code className="max-w-[10rem] truncate font-mono">{query.data.value}</code>
          <CopyButton value={query.data.value} />
        </>
      ) : (
        <Button variant="ghost" size="icon-sm" onClick={() => setRevealed(true)}>
          <Eye className="h-3.5 w-3.5" />
        </Button>
      )}
    </div>
  );
}
