"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useProviders } from "@/features/model-playground/api";
import type { Project } from "./api";
import { useProjectMutations } from "./api";

export function ProjectAiConfig({ project }: { project: Project }) {
  const providersQuery = useProviders();
  const { update } = useProjectMutations();

  const [provider, setProvider] = useState(project.default_provider ?? "");
  const [model, setModel] = useState(project.default_model ?? "");

  useEffect(() => {
    setProvider(project.default_provider ?? "");
    setModel(project.default_model ?? "");
  }, [project.default_provider, project.default_model]);

  if (providersQuery.isLoading) {
    return (
      <Card>
        <CardContent>
          <Skeleton className="h-9 w-full" />
        </CardContent>
      </Card>
    );
  }

  const providers = providersQuery.data ?? [];
  const selectedProvider = providers.find((p) => p.provider === provider);

  async function save(nextProvider: string, nextModel: string) {
    try {
      await update.mutateAsync({
        id: project.id,
        input: { default_provider: nextProvider, default_model: nextModel },
      });
      toast.success("Default AI provider updated");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update AI configuration");
    }
  }

  async function clear() {
    setProvider("");
    setModel("");
    try {
      await update.mutateAsync({ id: project.id, input: { clear_default_ai: true } });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to clear AI configuration");
    }
  }

  function handleProviderChange(next: string) {
    setProvider(next);
    setModel("");
  }

  function handleModelChange(next: string) {
    setModel(next);
    if (provider && next) save(provider, next);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Sparkles className="h-4 w-4" /> Default AI provider
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {/* value is always a defined string ("" for unselected), never
              undefined - Base UI (like React) decides controlled vs.
              uncontrolled on first render and warns if that ever flips. */}
          <Select value={provider} onValueChange={(v) => handleProviderChange(String(v))}>
            <SelectTrigger className="w-48">
              {/* Select.Value renders the raw item `value` (provider key,
                  e.g. "openai"), not its label, unless given a render
                  function - see Base UI SelectValueProps.children. */}
              <SelectValue placeholder="Choose a provider">
                {(v: string) => providers.find((p) => p.provider === v)?.display_name ?? "Choose a provider"}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {providers.map((p) => (
                <SelectItem key={p.provider} value={p.provider}>
                  {p.display_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={model} onValueChange={(v) => handleModelChange(String(v))} disabled={!provider}>
            <SelectTrigger className="w-56">
              <SelectValue placeholder="Choose a model" />
            </SelectTrigger>
            <SelectContent>
              {(selectedProvider?.models ?? []).map((m) => (
                <SelectItem key={m} value={m}>
                  {m}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {project.default_provider ? (
            <Button variant="ghost" size="sm" onClick={clear} disabled={update.isPending}>
              Clear
            </Button>
          ) : null}
        </div>

        {selectedProvider ? (
          selectedProvider.configured ? (
            <Badge variant="secondary" className="w-fit">
              Configured — ready to run
            </Badge>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="w-fit text-muted-foreground">
                Not configured
              </Badge>
              <Link href="/model-playground" className="text-xs text-muted-foreground underline underline-offset-2">
                Add an API key in Model Playground
              </Link>
            </div>
          )
        ) : (
          <p className="text-sm text-muted-foreground">No default provider set for this project yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
