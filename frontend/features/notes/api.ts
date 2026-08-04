import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export interface Note {
  id: string;
  title: string;
  content: string;
  color: string;
  pos_x: number;
  pos_y: number;
  width: number;
  height: number;
  z_index: number;
  pinned: boolean;
  archived: boolean;
  project_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface NoteCreateInput {
  title?: string;
  content?: string;
  color?: string;
  pos_x?: number;
  pos_y?: number;
  width?: number;
  height?: number;
  project_id?: string | null;
}

export interface NoteUpdateInput {
  title?: string;
  content?: string;
  color?: string;
  pos_x?: number;
  pos_y?: number;
  width?: number;
  height?: number;
  z_index?: number;
  pinned?: boolean;
  archived?: boolean;
  project_id?: string | null;
}

export const notesApi = {
  list: (archived = false, projectId?: string) =>
    api.get<Note[]>(`/api/notes?archived=${archived}${projectId ? `&project_id=${projectId}` : ""}`),
  search: (q: string) => api.get<Note[]>(`/api/notes/search?q=${encodeURIComponent(q)}`),
  create: (input: NoteCreateInput) => api.post<Note>("/api/notes", input),
  update: (id: string, input: NoteUpdateInput) => api.patch<Note>(`/api/notes/${id}`, input),
  remove: (id: string) => api.delete<void>(`/api/notes/${id}`),
};

export function useNotes(archived: boolean, projectId?: string) {
  return useQuery({ queryKey: ["notes", { archived, projectId }], queryFn: () => notesApi.list(archived, projectId) });
}

export function useNoteSearch(query: string) {
  return useQuery({
    queryKey: ["notes", "search", query],
    queryFn: () => notesApi.search(query),
    enabled: query.trim().length > 0,
  });
}

export function useNoteMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["notes"] });

  return {
    create: useMutation({ mutationFn: notesApi.create, onSuccess: invalidate }),
    update: useMutation({
      mutationFn: ({ id, input }: { id: string; input: NoteUpdateInput }) => notesApi.update(id, input),
      onSuccess: invalidate,
    }),
    remove: useMutation({ mutationFn: notesApi.remove, onSuccess: invalidate }),
  };
}
