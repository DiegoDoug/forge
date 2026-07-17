"use client";

import { CheckCircle2, Download, Eye, FileText, Loader2, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatBytes } from "@/lib/format";
import type { IngestJob } from "./api";

export function JobList({ job, onPreview }: { job: IngestJob; onPreview: (fileId: string) => void }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {job.files.filter((f) => f.status === "done").length} of {job.files.length} converted
        </p>
        {job.download_all_url ? (
          <Button variant="outline" size="sm" render={<a href={job.download_all_url} download />}>
            <Download className="h-3.5 w-3.5" />
            Download all (.zip)
          </Button>
        ) : null}
      </div>

      <div className="overflow-hidden rounded-xl border border-border">
        {job.files.map((file, i) => (
          <div
            key={file.id}
            className={`flex items-center gap-3 px-4 py-2.5 text-sm ${i > 0 ? "border-t border-border" : ""}`}
          >
            <StatusIcon status={file.status} />
            <span className="flex-1 truncate">{file.name}</span>
            {file.used_vision ? (
              <Badge variant="secondary" className="shrink-0">
                vision
              </Badge>
            ) : null}
            {file.status === "error" ? (
              <span className="shrink-0 text-xs text-destructive">{file.error}</span>
            ) : file.status === "done" ? (
              <>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {file.output_size ? formatBytes(file.output_size) : ""}
                </span>
                <Button variant="ghost" size="icon-sm" onClick={() => onPreview(file.id)}>
                  <Eye className="h-3.5 w-3.5" />
                </Button>
                {file.download_url ? (
                  <Button variant="ghost" size="icon-sm" render={<a href={file.download_url} download />}>
                    <Download className="h-3.5 w-3.5" />
                  </Button>
                ) : null}
              </>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusIcon({ status }: { status: string }) {
  if (status === "done") return <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />;
  if (status === "error") return <XCircle className="h-4 w-4 shrink-0 text-destructive" />;
  if (status === "processing") return <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />;
  return <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />;
}
