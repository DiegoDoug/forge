"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { ErrorState } from "@/components/error-state";
import { PageHeader } from "@/components/page-header";
import { SectionHeading } from "@/components/section-heading";
import { CONVERTER_TOOL_PROVIDERS } from "@/features/converters/providers";
import { Dropzone } from "@/features/ingest/dropzone";
import { ingestApi } from "@/features/ingest/api";
import { JobList } from "@/features/ingest/job-list";
import { PreviewSheet } from "@/features/ingest/preview-sheet";

export default function ConvertersPage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [previewFileId, setPreviewFileId] = useState<string | null>(null);

  const createJob = useMutation({
    mutationFn: ingestApi.createJob,
    onSuccess: (job) => setJobId(job.id),
    onError: (err) => toast.error(err instanceof Error ? err.message : "Upload failed"),
  });

  const jobQuery = useQuery({
    queryKey: ["ingest", "job", jobId],
    queryFn: () => ingestApi.getJob(jobId as string),
    enabled: Boolean(jobId),
    refetchInterval: (query) => (query.state.data?.status === "processing" ? 800 : false),
  });

  return (
    <div>
      <PageHeader title="Converter" description="Text, data & document conversion" />

      <div className="flex flex-col gap-8 p-4 md:p-6">
        <section className="flex flex-col gap-4">
          <SectionHeading>Text &amp; Data</SectionHeading>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {CONVERTER_TOOL_PROVIDERS.map(({ slug, Component }) => (
              <Component key={slug} />
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <SectionHeading>Documents</SectionHeading>
          <Dropzone onFiles={(files) => createJob.mutate(files)} disabled={createJob.isPending} />
          {createJob.isPending ? (
            <p className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Uploading…
            </p>
          ) : null}
          {jobQuery.isError ? (
            <ErrorState description="Couldn't check on your conversion job." onRetry={() => jobQuery.refetch()} />
          ) : jobQuery.data ? (
            <JobList job={jobQuery.data} onPreview={setPreviewFileId} />
          ) : null}
        </section>
      </div>

      <PreviewSheet jobId={jobId} fileId={previewFileId} onClose={() => setPreviewFileId(null)} />
    </div>
  );
}
