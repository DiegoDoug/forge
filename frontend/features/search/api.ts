import { api } from "@/lib/api-client";

export interface SearchSecretResult {
  id: string;
  name: string;
  type: string;
  folder_id: string | null;
}

export interface SearchNoteResult {
  id: string;
  title: string;
  excerpt: string;
}

export interface SearchResults {
  secrets: SearchSecretResult[];
  notes: SearchNoteResult[];
}

export const searchApi = {
  search: (q: string) => api.get<SearchResults>(`/api/search?q=${encodeURIComponent(q)}`),
};
