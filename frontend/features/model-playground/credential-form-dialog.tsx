"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCredentialMutations } from "./api";

export function CredentialFormDialog({
  open,
  onOpenChange,
  provider,
  displayName,
  configured,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  provider: string;
  displayName: string;
  configured: boolean;
}) {
  const [label, setLabel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const { create } = useCredentialMutations();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!apiKey.trim()) return;
    try {
      await create.mutateAsync({ provider, label: label.trim() || null, api_key: apiKey.trim() });
      toast.success(`${displayName} key saved`);
      setLabel("");
      setApiKey("");
      onOpenChange(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save key");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{configured ? `Replace ${displayName} key` : `Configure ${displayName}`}</DialogTitle>
            <DialogDescription>
              The key is encrypted at rest and never shown again after saving — replace or remove it, not view it.
            </DialogDescription>
          </DialogHeader>

          <div className="mt-4 flex flex-col gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="credential-label">Label (optional)</Label>
              <Input
                id="credential-label"
                placeholder={displayName}
                value={label}
                onChange={(e) => setLabel(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="credential-api-key">API key</Label>
              <Input
                id="credential-api-key"
                type="password"
                autoComplete="off"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                required
              />
            </div>
          </div>

          <DialogFooter>
            <DialogClose render={<Button type="button" variant="outline" />}>Cancel</DialogClose>
            <Button type="submit" disabled={create.isPending || !apiKey.trim()}>
              Save
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
