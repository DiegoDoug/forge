"use client";

import { CheckCircle2, Download, Eye, FileText, Loader2, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataList, DataListRow } from "@/components/data-list";
import { StatusBadge } from "@/components/status-badge";
import { formatBytes } from "@/lib/format";
import type { IngestJob } from "./api";

// Uploading is Converter's own inline state (page.tsx, while the create
// mutation is pending); this is the polling state once a job exists —
// processing/done/failed at the job level, alongside the per-file status
// icons already shown per row (02_UI.md §3.10).
function JobStatusBadge({ status }: { status: IngestJob["status"] }) {
  if (status === "done") return <StatusBadge tone="success">Complete</StatusBadge>;
  if (status === "failed") return <StatusBadge tone="danger">Failed</StatusBadge>;
  return <StatusBadge tone="info" icon={Loader2}>Processing</StatusBadge>;
}

export function JobList({ job, onPreview }: { job: IngestJob; onPreview: (fileId: string) => void }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <JobStatusBadge status={job.status} />
          <p className="text-xs text-muted-foreground">
            {job.files.filter((f) => f.status === "done").length} of {job.files.length} converted
          </p>
        </div>
        {job.download_all_url ? (
          <Button variant="outline" size="sm" nativeButton={false} render={<a href={job.download_all_url} download />}>
            <Download className="h-3.5 w-3.5" />
            Download all (.zip)
          </Button>
        ) : null}
      </div>

      <DataList>
        {job.files.map((file) => (
          <DataListRow key={file.id}>
            <StatusIcon status={file.status} />
            <span className="data-primary flex-1 truncate">{file.name}</span>
            {file.used_vision ? (
              <Badge variant="secondary" className="shrink-0">
                vision
              </Badge>
            ) : null}
            {file.status === "error" ? (
              <span className="data-meta shrink-0 text-destructive">{file.error}</span>
            ) : file.status === "done" ? (
              <>
                <span className="data-meta shrink-0">{file.output_size ? formatBytes(file.output_size) : ""}</span>
                <Button variant="ghost" size="icon-sm" onClick={() => onPreview(file.id)}>
                  <Eye className="h-3.5 w-3.5" />
                </Button>
                {file.download_url ? (
                  <Button variant="ghost" size="icon-sm" nativeButton={false} render={<a href={file.download_url} download />}>
                    <Download className="h-3.5 w-3.5" />
                  </Button>
                ) : null}
              </>
            ) : null}
          </DataListRow>
        ))}
      </DataList>
    </div>
  );
}

function StatusIcon({ status }: { status: string }) {
  if (status === "done") return <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />;
  if (status === "error") return <XCircle className="h-4 w-4 shrink-0 text-destructive" />;
  if (status === "processing") return <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />;
  return <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />;
}
