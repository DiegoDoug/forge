"use client";

import { useState } from "react";
import { KeyRound, Trash2 } from "lucide-react";
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
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCredentialMutations, useCredentials, useProviders } from "./api";
import { CredentialFormDialog } from "./credential-form-dialog";

export function ProviderList() {
  const providersQuery = useProviders();
  const credentialsQuery = useCredentials();
  const { remove } = useCredentialMutations();
  const [configuringProvider, setConfiguringProvider] = useState<string | null>(null);

  async function handleRemove(credentialId: string, displayName: string) {
    try {
      await remove.mutateAsync(credentialId);
      toast.success(`${displayName} key removed`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to remove key");
    }
  }

  if (providersQuery.isLoading) {
    return (
      <Card>
        <CardContent className="flex flex-col gap-2">
          <Skeleton className="h-9 w-full" />
          <Skeleton className="h-9 w-full" />
        </CardContent>
      </Card>
    );
  }

  const providers = providersQuery.data ?? [];
  const credentialsByProvider = new Map((credentialsQuery.data?.items ?? []).map((c) => [c.provider, c]));
  const configuring = providers.find((p) => p.provider === configuringProvider);

  return (
    <Card>
      <CardContent className="flex flex-col divide-y divide-border p-0">
        {providers.map((provider) => {
          const credential = credentialsByProvider.get(provider.provider);
          return (
            <div key={provider.provider} className="flex items-center justify-between gap-3 px-4 py-3">
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
                  <AlertDialog>
                    <AlertDialogTrigger render={<Button variant="ghost" size="icon-sm" className="text-destructive" />}>
                      <Trash2 className="h-3.5 w-3.5" />
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Remove {provider.display_name} key?</AlertDialogTitle>
                        <AlertDialogDescription>
                          {provider.display_name} becomes unavailable for new runs. Past runs that used it are
                          unaffected.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          className="bg-destructive text-white hover:bg-destructive/90"
                          onClick={() => handleRemove(credential.id, provider.display_name)}
                        >
                          Remove
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                ) : null}
              </div>
            </div>
          );
        })}
      </CardContent>

      {configuring ? (
        <CredentialFormDialog
          open={Boolean(configuringProvider)}
          onOpenChange={(open) => setConfiguringProvider(open ? configuringProvider : null)}
          provider={configuring.provider}
          displayName={configuring.display_name}
          configured={configuring.configured}
        />
      ) : null}
    </Card>
  );
}
