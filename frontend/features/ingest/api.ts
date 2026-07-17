import { api } from "@/lib/api-client";

export interface IngestFileTask {
  id: string;
  name: string;
  markdown_name: string;
  status: "pending" | "processing" | "done" | "error";
  error: string | null;
  output_size: number | null;
  used_vision: boolean;
  download_url: string | null;
}

export interface IngestJob {
  id: string;
  status: "processing" | "done" | "failed";
  progress: number;
  files: IngestFileTask[];
  download_all_url: string | null;
}

export const ingestApi = {
  formats: () => api.get<{ extensions: string[] }>("/api/ingest/formats"),
  createJob: (files: File[]) => {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return api.upload<IngestJob>("/api/ingest/jobs", form);
  },
  getJob: (jobId: string) => api.get<IngestJob>(`/api/ingest/jobs/${jobId}`),
  getFileContent: (jobId: string, fileId: string) =>
    api.get<{ name: string; markdown: string }>(`/api/ingest/jobs/${jobId}/files/${fileId}/content`),
  saveToNotes: (jobId: string, fileId: string, color?: string) =>
    api.post(`/api/ingest/jobs/${jobId}/files/${fileId}/save-to-notes`, { color }),
};
