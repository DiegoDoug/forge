import { api } from "@/lib/api-client";

export interface McpToken {
  id: string;
  name: string;
  scopes: string[];
  created_at: string;
  last_used_at: string | null;
  revoked_at: string | null;
}

export interface McpTokenCreated extends McpToken {
  token: string;
}

export const MCP_SCOPES: { value: string; label: string; disabled?: boolean }[] = [
  { value: "forge:read", label: "Read" },
  { value: "forge:write", label: "Write" },
  { value: "forge:delete", label: "Delete" },
  { value: "forge:secrets", label: "Secrets (reserved — unused)", disabled: true },
];

export const mcpTokensApi = {
  list: () => api.get<McpToken[]>("/api/mcp/tokens"),
  create: (name: string, scopes: string[]) => api.post<McpTokenCreated>("/api/mcp/tokens", { name, scopes }),
  revoke: (id: string) => api.delete<void>(`/api/mcp/tokens/${id}`),
};
