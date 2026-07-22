"use client";

import { useState } from "react";

import { PageHeader } from "@/components/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { AiInstructionsForm } from "@/features/project-init/ai-instructions-form";
import { useProjectInitCatalog, type TemplateKind } from "@/features/project-init/api";
import { FdkPhaseForm } from "@/features/project-init/fdk-phase-form";
import { FilePreview } from "@/features/project-init/file-preview";
import { GenerationHistory } from "@/features/project-init/generation-history";
import { KindPicker } from "@/features/project-init/kind-picker";

export default function ProjectInitPage() {
  const { data: catalog, isLoading, isError } = useProjectInitCatalog();
  const [selectedKind, setSelectedKind] = useState<TemplateKind | null>(null);

  return (
    <div>
      <PageHeader
        title="Project Init"
        description="Generate FDK phase scaffolds and AI project instruction files."
      />
      <div className="flex flex-col gap-6 p-4 md:p-6">
        {isLoading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <Skeleton className="h-24 w-full rounded-xl" />
            <Skeleton className="h-24 w-full rounded-xl" />
          </div>
        ) : isError || !catalog ? (
          <p className="text-sm text-destructive">Couldn&apos;t load the template catalog. Try reloading the page.</p>
        ) : (
          <>
            <KindPicker kinds={catalog.kinds} selected={selectedKind} onSelect={setSelectedKind} />

            {selectedKind === null ? (
              <p className="text-sm text-muted-foreground">Pick a template to get started.</p>
            ) : (
              <div className="flex flex-col gap-4 rounded-xl border border-border p-4">
                {selectedKind === "fdk_phase" ? (
                  <FdkPhaseForm onGenerated={() => {}} />
                ) : (
                  <AiInstructionsForm onGenerated={() => {}} />
                )}
                <FilePreview kind={selectedKind} catalog={catalog.kinds} />
              </div>
            )}
          </>
        )}

        <div className="flex flex-col gap-3">
          <h2 className="text-sm font-medium">Recent generations</h2>
          <GenerationHistory />
        </div>
      </div>
    </div>
  );
}
