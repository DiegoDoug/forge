"use client";

import { useState } from "react";
import { ChevronDown, KeyRound, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { ErrorState } from "@/components/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useCredentialMutations, useCredentials, useProviders } from "./api";
import { CredentialFormDialog } from "./credential-form-dialog";

// Provider configuration is setup, not the moment-to-moment task of this
// screen (that's composing and comparing runs — PromptComposer already
// carries per-run model selection). Collapsing it behind a summary keeps it
// reachable without letting a one-time setup panel outweigh the actual
// execution/comparison workspace (Phase 10 UX elevation).
export function ProviderListSummary() {
  const providersQuery = useProviders();
  const [expanded, setExpanded] = useState(false);

  if (providersQuery.isLoading) {
    return (
      <Card>
        <CardContent className="flex flex-col gap-2">
          <Skeleton className="h-9 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (providersQuery.isError) {
    return (
      <Card>
        <CardContent>
          <ErrorState description="Couldn't load providers." onRetry={() => providersQuery.refetch()} />
        </CardContent>
      </Card>
    );
  }

  const providers = providersQuery.data ?? [];
  const configuredCount = providers.filter((p) => p.configured).length;
  // Nothing configured yet blocks the primary task (PromptComposer can't
  // run anything) — start expanded so setup is immediately visible instead
  // of one extra click away from an otherwise-empty screen.
  const isOpen = expanded || configuredCount === 0;

  return (
    <Card>
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2 text-sm">
          <KeyRound className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">Providers</span>
          <span className="text-xs text-muted-foreground">
            {configuredCount} of {providers.length} configured
          </span>
        </div>
        <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform", isOpen && "rotate-180")} />
      </button>
      {isOpen ? <ProviderList /> : null}
    </Card>
  );
}

export function ProviderList() {
  const providersQuery = useProviders();
  const credentialsQuery = useCredentials();
  const { remove } = useCredentialMutations();
  const [configuringProvider, setConfiguringProvider] = useState<string | null>(null);
  const [removeTarget, setRemoveTarget] = useState<{ credentialId: string; displayName: string } | null>(null);

  async function handleRemove() {
    if (!removeTarget) return;
    const { credentialId, displayName } = removeTarget;
    setRemoveTarget(null);
    try {
      await remove.mutateAsync(credentialId);
      toast.success(`${displayName} key removed`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to remove key");
    }
  }

  if (providersQuery.isLoading) {
    return (
      <div className="flex flex-col gap-2 border-t border-border p-4">
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-9 w-full" />
      </div>
    );
  }

  if (providersQuery.isError) {
    return (
      <div className="border-t border-border p-4">
        <ErrorState description="Couldn't load providers." onRetry={() => providersQuery.refetch()} />
      </div>
    );
  }

  const providers = providersQuery.data ?? [];
  const credentialsByProvider = new Map((credentialsQuery.data?.items ?? []).map((c) => [c.provider, c]));
  const configuring = providers.find((p) => p.provider === configuringProvider);

  return (
    <>
      <div className="flex flex-col divide-y divide-border border-t border-border">
        {providers.map((provider) => {
          const credential = credentialsByProvider.get(provider.provider);
          return (
            <div key={provider.provider} className="flex items-center justify-between gap-3 px-4 py-3">
              <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{provider.display_name}</span>
                  {provider.configured ? (
                    <Badge variant="secondary">Configured</Badge>
                  ) : (
                    <Badge variant="outline" className="text-muted-foreground">
                      Not configured
                    </Badge>
                  )}
                </div>
                {provider.configured && credential?.base_url ? (
                  <span className="text-xs text-muted-foreground">{credential.base_url}</span>
                ) : null}
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant={provider.configured ? "outline" : "default"}
                  size="sm"
                  onClick={() => setConfiguringProvider(provider.provider)}
                >
                  <KeyRound className="h-3.5 w-3.5" />
                  {provider.configured ? "Replace key" : "Configure"}
                </Button>
                {provider.configured && credential ? (
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    className="text-destructive"
                    onClick={() => setRemoveTarget({ credentialId: credential.id, displayName: provider.display_name })}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>

      {configuring ? (
        <CredentialFormDialog
          open={Boolean(configuringProvider)}
          onOpenChange={(open) => setConfiguringProvider(open ? configuringProvider : null)}
          provider={configuring}
        />
      ) : null}

      <ConfirmDialog
        open={!!removeTarget}
        onOpenChange={(open) => !open && setRemoveTarget(null)}
        title={`Remove ${removeTarget?.displayName} key?`}
        description={`${removeTarget?.displayName} becomes unavailable for new runs. Past runs that used it are unaffected.`}
        confirmLabel="Remove"
        onConfirm={handleRemove}
      />
    </>
  );
}
