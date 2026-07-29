"use client";

import { useState } from "react";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { MAX_TARGETS_PER_RUN, type RunTarget, useProviders } from "./api";

function targetKey(target: RunTarget): string {
  return `${target.provider}:${target.model}`;
}

export function PromptComposer({
  onSubmit,
  isSubmitting,
}: {
  onSubmit: (prompt: string, targets: RunTarget[]) => void;
  isSubmitting: boolean;
}) {
  const providersQuery = useProviders();
  const [prompt, setPrompt] = useState("");
  const [selected, setSelected] = useState<RunTarget[]>([]);

  const configuredProviders = (providersQuery.data ?? []).filter((p) => p.configured);
  const atCap = selected.length >= MAX_TARGETS_PER_RUN;

  function toggle(target: RunTarget, checked: boolean) {
    setSelected((prev) => {
      if (checked) {
        if (prev.some((t) => targetKey(t) === targetKey(target))) return prev;
        if (prev.length >= MAX_TARGETS_PER_RUN) return prev;
        return [...prev, target];
      }
      return prev.filter((t) => targetKey(t) !== targetKey(target));
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!prompt.trim() || selected.length === 0) return;
    onSubmit(prompt.trim(), selected);
  }

  if (providersQuery.isLoading) {
    return (
      <Card>
        <CardContent className="flex flex-col gap-2">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-9 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <Textarea
            placeholder="Write a prompt to send to every selected provider/model…"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="min-h-28"
          />

          {configuredProviders.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Configure at least one provider above to run a comparison.
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {configuredProviders.map((provider) => (
                <div key={provider.provider} className="flex flex-col gap-1.5">
                  <span className="text-xs font-medium text-muted-foreground">{provider.display_name}</span>
                  <div className="flex flex-wrap gap-x-4 gap-y-1.5">
                    {provider.models.map((model) => {
                      const target = { provider: provider.provider, model };
                      const key = targetKey(target);
                      const checked = selected.some((t) => targetKey(t) === key);
                      return (
                        <div key={key} className="flex items-center gap-1.5">
                          <Checkbox
                            id={key}
                            checked={checked}
                            disabled={!checked && atCap}
                            onCheckedChange={(value) => toggle(target, value === true)}
                          />
                          <Label htmlFor={key} className="text-sm font-normal">
                            {model}
                          </Label>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              {selected.length}/{MAX_TARGETS_PER_RUN} selected
            </span>
            <Button
              type="submit"
              size="sm"
              disabled={isSubmitting || !prompt.trim() || selected.length === 0}
            >
              <Send className="h-3.5 w-3.5" />
              Run comparison
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
