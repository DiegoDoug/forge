"use client";

import { useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ProviderListSummary } from "@/features/model-playground/provider-list";
import { RunHistoryList } from "@/features/model-playground/run-history-list";
import { RunView } from "@/features/model-playground/run-view";

export default function ModelPlaygroundPage() {
  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  return (
    <div className="flex flex-col">
      <PageHeader title="Model Playground" description="Compare LLM provider outputs side by side" />

      <div className="grid grid-cols-1 gap-6 p-4 md:p-6 lg:grid-cols-[1fr_20rem]">
        <div className="flex flex-col gap-4">
          <ProviderListSummary />
          <RunView activeRunId={activeRunId} onRunCreated={setActiveRunId} />
        </div>

        <div className="flex flex-col gap-2">
          <h2 className="text-sm font-medium text-muted-foreground">History</h2>
          <RunHistoryList activeRunId={activeRunId} onSelect={setActiveRunId} />
        </div>
      </div>
    </div>
  );
}
