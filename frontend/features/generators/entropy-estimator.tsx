"use client";

import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { generatorsApi } from "./api";

const STRENGTH_COLOR: Record<string, string> = {
  empty: "[&>div]:bg-muted-foreground",
  "very weak": "[&>div]:bg-destructive",
  weak: "[&>div]:bg-orange-500",
  reasonable: "[&>div]:bg-yellow-500",
  strong: "[&>div]:bg-lime-500",
  "very strong": "[&>div]:bg-emerald-500",
};

export function EntropyEstimator() {
  const [value, setValue] = useState("");
  const estimate = useMutation({ mutationFn: generatorsApi.entropy });

  useEffect(() => {
    const handle = setTimeout(() => {
      if (value) estimate.mutate({ value });
    }, 250);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const bits = estimate.data?.bits ?? 0;
  const strength = estimate.data?.strength ?? "empty";

  return (
    <ToolCard title="Entropy estimator" description="Paste any string to estimate its guessing resistance">
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type or paste a password…"
        className="font-mono text-xs"
        rows={2}
      />
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="capitalize">{strength}</span>
          <span>{bits} bits</span>
        </div>
        <Progress value={Math.min(100, (bits / 128) * 100)} className={`h-1.5 ${STRENGTH_COLOR[strength]}`} />
      </div>
    </ToolCard>
  );
}
