"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, Plus } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ConfirmDialog } from "@/components/confirm-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { ToolCard } from "@/components/tool-card";
import { formatRelativeTime } from "@/lib/format";
import { useClipboard } from "@/hooks/use-clipboard";
import { MCP_SCOPES, mcpTokensApi, type McpToken } from "@/features/mcp-tokens/api";

export function McpTokensCard() {
  const queryClient = useQueryClient();
  const { copy } = useClipboard();
  const tokensQuery = useQuery({ queryKey: ["mcp-tokens"], queryFn: mcpTokensApi.list });

  const [name, setName] = useState("");
  const [scopes, setScopes] = useState<string[]>(["forge:read"]);
  const [createdToken, setCreatedToken] = useState<{ name: string; token: string } | null>(null);
  const [revokeTarget, setRevokeTarget] = useState<McpToken | null>(null);

  const createMutation = useMutation({
    mutationFn: () => mcpTokensApi.create(name.trim(), scopes),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["mcp-tokens"] });
      setCreatedToken({ name: result.name, token: result.token });
      setName("");
      setScopes(["forge:read"]);
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to create token"),
  });

  const revokeMutation = useMutation({
    mutationFn: (id: string) => mcpTokensApi.revoke(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mcp-tokens"] });
      toast.success("Token revoked");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to revoke token"),
    onSettled: () => setRevokeTarget(null),
  });

  function toggleScope(scope: string, checked: boolean) {
    setScopes((prev) => (checked ? [...prev, scope] : prev.filter((s) => s !== scope)));
  }

  const tokens = tokensQuery.data ?? [];
  const active = tokens.filter((t) => !t.revoked_at);
  const revoked = tokens.filter((t) => t.revoked_at);

  return (
    <ToolCard
      title="Claude / MCP access"
      description="Bearer tokens Claude uses to connect to Forge's MCP server — scoped and individually revocable, never the same credential as your browser session."
      className="md:col-span-2"
    >
      <div className="flex flex-col gap-4">
        {tokensQuery.isLoading ? (
          <p className="text-xs text-muted-foreground">Loading…</p>
        ) : active.length === 0 ? (
          <p className="text-xs text-muted-foreground">No active tokens yet.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {active.map((token) => (
              <div
                key={token.id}
                className="flex items-center justify-between gap-3 rounded-lg border border-border px-3 py-2"
              >
                <div className="flex flex-col gap-1">
                  <span className="text-sm font-medium">{token.name}</span>
                  <div className="flex flex-wrap items-center gap-1">
                    {token.scopes.length === 0 ? (
                      <span className="text-xs text-muted-foreground">no scopes</span>
                    ) : (
                      token.scopes.map((s) => (
                        <Badge key={s} variant="outline" className="text-[10px]">
                          {s}
                        </Badge>
                      ))
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    Created {formatRelativeTime(token.created_at)}
                    {token.last_used_at ? ` · last used ${formatRelativeTime(token.last_used_at)}` : " · never used"}
                  </span>
                </div>
                <Button variant="outline" size="sm" onClick={() => setRevokeTarget(token)}>
                  Revoke
                </Button>
              </div>
            ))}
          </div>
        )}

        {revoked.length > 0 ? (
          <details className="text-xs text-muted-foreground">
            <summary className="cursor-pointer select-none">
              {revoked.length} revoked token{revoked.length === 1 ? "" : "s"}
            </summary>
            <div className="mt-2 flex flex-col gap-1">
              {revoked.map((token) => (
                <div key={token.id} className="flex items-center justify-between">
                  <span>{token.name}</span>
                  <span>revoked {token.revoked_at ? formatRelativeTime(token.revoked_at) : ""}</span>
                </div>
              ))}
            </div>
          </details>
        ) : null}

        <Separator />

        <div className="flex flex-col gap-2">
          <Label htmlFor="mcp-token-name" className="text-xs text-muted-foreground">
            New token name
          </Label>
          <Input
            id="mcp-token-name"
            placeholder="e.g. Claude Code — dev laptop"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <div className="flex flex-wrap gap-3">
            {MCP_SCOPES.map((scope) => (
              <label key={scope.value} className="flex items-center gap-1.5 text-xs">
                <Checkbox
                  checked={scopes.includes(scope.value)}
                  disabled={scope.disabled}
                  onCheckedChange={(checked) => toggleScope(scope.value, checked === true)}
                />
                {scope.label}
              </label>
            ))}
          </div>
          <Button
            size="sm"
            className="w-fit"
            onClick={() => createMutation.mutate()}
            disabled={!name.trim() || createMutation.isPending}
          >
            <Plus className="h-3.5 w-3.5" />
            Create token
          </Button>
        </div>
      </div>

      <Dialog open={!!createdToken} onOpenChange={(open) => !open && setCreatedToken(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Token created</DialogTitle>
            <DialogDescription>
              Copy this now — it&apos;s shown exactly once and can&apos;t be retrieved again. Configure Claude Code
              with: <code className="text-[11px]">claude mcp add --transport http forge &lt;your-forge-url&gt;/mcp
              --header &quot;Authorization: Bearer &lt;token&gt;&quot;</code>
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 p-2">
            <code className="flex-1 overflow-x-auto text-xs">{createdToken?.token}</code>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => createdToken && copy(createdToken.token)}
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
          <DialogFooter showCloseButton />
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!revokeTarget}
        onOpenChange={(open) => !open && setRevokeTarget(null)}
        title={`Revoke "${revokeTarget?.name}"?`}
        description="Claude will no longer be able to connect using this token. This cannot be undone — provision a new token if Claude needs access again."
        confirmLabel="Revoke"
        onConfirm={() => revokeTarget && revokeMutation.mutate(revokeTarget.id)}
      />
    </ToolCard>
  );
}
