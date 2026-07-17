"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { Dropzone } from "@/features/ingest/dropzone";
import { ingestApi } from "@/features/ingest/api";
import { JobList } from "@/features/ingest/job-list";
import { PreviewSheet } from "@/features/ingest/preview-sheet";

export default function IngestPage() {
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
      <PageHeader title="Ingest" description="Convert documents into clean, AI-optimized Markdown" />

      <div className="flex flex-col gap-4 p-4 md:p-6">
        <Dropzone onFiles={(files) => createJob.mutate(files)} disabled={createJob.isPending} />

        {jobQuery.data ? <JobList job={jobQuery.data} onPreview={setPreviewFileId} /> : null}
      </div>

      <PreviewSheet jobId={jobId} fileId={previewFileId} onClose={() => setPreviewFileId(null)} />
    </div>
  );
}
