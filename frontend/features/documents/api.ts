import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export const EXPORT_FORMATS = ["txt", "md", "doc", "docx", "pdf", "xml"] as const;
export type ExportFormat = (typeof EXPORT_FORMATS)[number];

export interface DocumentSummary {
  id: string;
  title: string;
  pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface Document extends DocumentSummary {
  content: string;
}

export interface DocumentCreateInput {
  title?: string;
  content?: string;
  pinned?: boolean;
}

export interface DocumentUpdateInput {
  title?: string;
  content?: string;
  pinned?: boolean;
}

export const documentsApi = {
  list: () => api.get<DocumentSummary[]>("/api/documents"),
  search: (q: string) => api.get<DocumentSummary[]>(`/api/documents/search?q=${encodeURIComponent(q)}`),
  get: (id: string) => api.get<Document>(`/api/documents/${id}`),
  create: (input: DocumentCreateInput) => api.post<Document>("/api/documents", input),
  update: (id: string, input: DocumentUpdateInput) => api.patch<Document>(`/api/documents/${id}`, input),
  remove: (id: string) => api.delete<void>(`/api/documents/${id}`),
  exportUrl: (id: string, format: ExportFormat) => `/api/documents/${id}/export?format=${format}`,
};

export function useDocuments() {
  return useQuery({ queryKey: ["documents"], queryFn: documentsApi.list });
}

export function useDocumentSearch(query: string) {
  return useQuery({
    queryKey: ["documents", "search", query],
    queryFn: () => documentsApi.search(query),
    enabled: query.trim().length > 0,
  });
}

export function useDocument(id: string | null) {
  return useQuery({
    queryKey: ["documents", id],
    queryFn: () => documentsApi.get(id as string),
    enabled: !!id,
  });
}

export function useDocumentMutations() {
  const qc = useQueryClient();
  const invalidateList = () => qc.invalidateQueries({ queryKey: ["documents"], exact: true });

  return {
    create: useMutation({ mutationFn: documentsApi.create, onSuccess: invalidateList }),
    update: useMutation({
      mutationFn: ({ id, input }: { id: string; input: DocumentUpdateInput }) => documentsApi.update(id, input),
      onSuccess: (doc) => {
        invalidateList();
        qc.setQueryData(["documents", doc.id], doc);
      },
    }),
    remove: useMutation({
      mutationFn: documentsApi.remove,
      onSuccess: (_data, id) => {
        invalidateList();
        qc.removeQueries({ queryKey: ["documents", id] });
      },
    }),
  };
}

/** Downloads a document export by fetching it as a blob (so the session
 * cookie goes along with the request) rather than a bare `<a href>`, which
 * wouldn't carry credentials to a same-origin API route reliably across
 * browsers once query params are involved. */
export async function downloadDocumentExport(id: string, format: ExportFormat, fallbackName: string) {
  const res = await fetch(documentsApi.exportUrl(id, format), { credentials: "include" });
  if (!res.ok) {
    throw new Error(`Export failed (${res.status})`);
  }
  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition") ?? "";
  const match = /filename="([^"]+)"/.exec(disposition);
  const filename = match?.[1] ?? `${fallbackName}.${format}`;

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
