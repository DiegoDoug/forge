"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { SecretDetail, SecretType } from "./api";
import { useVaultMutations } from "./api";
import { SECRET_TYPE_LABELS, SECRET_TYPES } from "./secret-types";

interface SecretFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  secret?: SecretDetail | null;
  folderId?: string | null;
  onSaved?: (id: string) => void;
}

export function SecretFormDialog({ open, onOpenChange, secret, folderId, onSaved }: SecretFormDialogProps) {
  const { createSecret, updateSecret } = useVaultMutations();
  const isEdit = Boolean(secret);

  const [name, setName] = useState("");
  const [type, setType] = useState<SecretType>("password");
  const [value, setValue] = useState("");
  const [username, setUsername] = useState("");
  const [url, setUrl] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (open) {
      setName(secret?.name ?? "");
      setType(secret?.type ?? "password");
      setValue(secret?.value ?? "");
      setUsername(secret?.metadata.username ?? "");
      setUrl(secret?.metadata.url ?? "");
      setNotes(secret?.metadata.notes ?? "");
    }
  }, [open, secret]);

  const pending = createSecret.isPending || updateSecret.isPending;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Name is required");
      return;
    }

    const metadata = { username: username || null, url: url || null, notes: notes || null };

    try {
      if (isEdit && secret) {
        const payload: Parameters<typeof updateSecret.mutateAsync>[0]["input"] = { name, type, metadata };
        if (value) payload.value = value;
        const updated = await updateSecret.mutateAsync({ id: secret.id, input: payload });
        onSaved?.(updated.id);
      } else {
        const created = await createSecret.mutateAsync({
          name,
          type,
          value,
          folder_id: folderId ?? null,
          metadata,
        });
        onSaved?.(created.id);
      }
      onOpenChange(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save secret");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <DialogHeader>
            <DialogTitle>{isEdit ? "Edit secret" : "New secret"}</DialogTitle>
            <DialogDescription>
              {isEdit ? "Update this vault entry." : "Values are encrypted at rest before they touch disk."}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="secret-name">Name</Label>
                <Input id="secret-name" value={name} onChange={(e) => setName(e.target.value)} autoFocus />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label>Type</Label>
                <Select value={type} onValueChange={(v) => v && setType(v as SecretType)}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SECRET_TYPES.map((t) => (
                      <SelectItem key={t} value={t}>
                        {SECRET_TYPE_LABELS[t]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="secret-value">Value {isEdit ? <span className="text-muted-foreground">(leave blank to keep current)</span> : null}</Label>
              <Textarea
                id="secret-value"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder={isEdit ? "••••••••••••" : "Secret value"}
                className="font-mono text-xs"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="secret-username">Username</Label>
                <Input id="secret-username" value={username} onChange={(e) => setUsername(e.target.value)} />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="secret-url">URL</Label>
                <Input id="secret-url" value={url} onChange={(e) => setUrl(e.target.value)} />
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="secret-notes">Notes</Label>
              <Textarea id="secret-notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
            </div>
          </div>

          <DialogFooter>
            <Button type="submit" disabled={pending}>
              {pending ? "Saving…" : isEdit ? "Save changes" : "Create secret"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
