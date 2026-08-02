"use client";

import { useState } from "react";
import { Loader2, PlugZap } from "lucide-react";
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
import { useCredentialMutations, useTestConnection, type ProviderAvailability } from "./api";

export function CredentialFormDialog({
  open,
  onOpenChange,
  provider,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  provider: ProviderAvailability;
}) {
  const { displayName, configured, requiresBaseUrl, allowsCustomModel, defaultModel } = {
    displayName: provider.display_name,
    configured: provider.configured,
    requiresBaseUrl: provider.requires_base_url,
    allowsCustomModel: provider.allows_custom_model,
    defaultModel: provider.models[0] ?? "",
  };

  const [label, setLabel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [testModel, setTestModel] = useState(defaultModel);
  const { create } = useCredentialMutations();
  const testConnection = useTestConnection();

  const canTest = apiKey.trim().length > 0 && (!requiresBaseUrl || baseUrl.trim().length > 0) && testModel.trim().length > 0;
  const canSave = apiKey.trim().length > 0 && (!requiresBaseUrl || baseUrl.trim().length > 0);

  function reset() {
    setLabel("");
    setApiKey("");
    setBaseUrl("");
    setTestModel(defaultModel);
    testConnection.reset();
  }

  async function handleTest() {
    try {
      const result = await testConnection.mutateAsync({
        provider: provider.provider,
        api_key: apiKey.trim(),
        base_url: requiresBaseUrl ? baseUrl.trim() : null,
        model: testModel.trim(),
      });
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Connection test failed");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSave) return;
    try {
      await create.mutateAsync({
        provider: provider.provider,
        label: label.trim() || null,
        api_key: apiKey.trim(),
        base_url: requiresBaseUrl ? baseUrl.trim() : null,
      });
      toast.success(`${displayName} key saved`);
      reset();
      onOpenChange(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save key");
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) reset();
        onOpenChange(next);
      }}
    >
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
              <Label htmlFor="credential-label">{requiresBaseUrl ? "Name" : "Label (optional)"}</Label>
              <Input
                id="credential-label"
                placeholder={displayName}
                value={label}
                onChange={(e) => setLabel(e.target.value)}
              />
            </div>

            {requiresBaseUrl ? (
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="credential-base-url">Base URL</Label>
                <Input
                  id="credential-base-url"
                  placeholder="https://example.com/v1"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  required
                />
              </div>
            ) : null}

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="credential-api-key">API key</Label>
              <Input
                id="credential-api-key"
                type="password"
                autoComplete="off"
                placeholder={configured ? "••••••••••••••••" : undefined}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                required
              />
            </div>

            {allowsCustomModel ? (
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="credential-test-model">Model (for testing the connection)</Label>
                <Input
                  id="credential-test-model"
                  placeholder="my-model"
                  value={testModel}
                  onChange={(e) => setTestModel(e.target.value)}
                />
              </div>
            ) : null}

            <Button
              type="button"
              variant="outline"
              size="sm"
              className="self-start"
              disabled={!canTest || testConnection.isPending}
              onClick={handleTest}
            >
              {testConnection.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <PlugZap className="h-3.5 w-3.5" />}
              Test Connection
            </Button>
          </div>

          <DialogFooter>
            <DialogClose render={<Button type="button" variant="outline" />}>Cancel</DialogClose>
            <Button type="submit" disabled={create.isPending || !canSave}>
              Save
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
