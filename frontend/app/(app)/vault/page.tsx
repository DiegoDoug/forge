"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { KeyRound, Plus, Search, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelativeTime } from "@/lib/format";
import { useSecrets, vaultApi, type SecretDetail } from "@/features/vault/api";
import { SECRET_TYPE_LABELS } from "@/features/vault/secret-types";
import { SecretDetailSheet } from "@/features/vault/secret-detail-sheet";
import { SecretFormDialog } from "@/features/vault/secret-form-dialog";
import { VaultFilters } from "@/features/vault/vault-filters";

export default function VaultPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const openId = searchParams.get("open");

  const [folderId, setFolderId] = useState<string | null>(null);
  const [tagId, setTagId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editSecret, setEditSecret] = useState<SecretDetail | null>(null);

  const secretsQuery = useSecrets({
    folder_id: folderId ?? undefined,
    tag_id: tagId ?? undefined,
    q: query || undefined,
  });

  const editQuery = useQuery({
    queryKey: ["vault", "secret", editSecret?.id, "edit"],
    queryFn: () => vaultApi.getSecret(editSecret!.id, true),
    enabled: Boolean(editSecret),
  });

  const closeDetail = () => router.push("/vault");

  async function startEdit(id: string) {
    const detail = await vaultApi.getSecret(id, true);
    setEditSecret(detail);
    setFormOpen(true);
  }

  const secrets = useMemo(() => secretsQuery.data ?? [], [secretsQuery.data]);

  return (
    <div>
      <PageHeader
        title="Vault"
        description="Encrypted secrets, API keys, and credentials"
        actions={
          <Button
            size="sm"
            onClick={() => {
              setEditSecret(null);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" />
            New secret
          </Button>
        }
      />

      <div className="flex">
        <VaultFilters folderId={folderId} tagId={tagId} onFolderChange={setFolderId} onTagChange={setTagId} />

        <div className="flex-1 p-4 md:p-6">
          <div className="mb-4 flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <Search className="pointer-events-none absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search secrets…"
                className="pl-8"
              />
            </div>
          </div>

          {secretsQuery.isLoading ? (
            <div className="flex flex-col gap-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : secrets.length === 0 ? (
            <EmptyState
              icon={KeyRound}
              title="No secrets here yet"
              description="Store passwords, API keys, SSH keys, and other credentials — encrypted at rest."
              action={
                <Button size="sm" onClick={() => setFormOpen(true)}>
                  <Plus className="h-4 w-4" />
                  New secret
                </Button>
              }
            />
          ) : (
            <div className="overflow-hidden rounded-xl border border-border">
              {secrets.map((secret, i) => (
                <button
                  key={secret.id}
                  onClick={() => router.push(`/vault?open=${secret.id}`)}
                  className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm transition-colors hover:bg-accent/40 ${
                    i > 0 ? "border-t border-border" : ""
                  }`}
                >
                  {secret.favorite ? (
                    <Star className="h-3.5 w-3.5 shrink-0 fill-primary text-primary" />
                  ) : (
                    <KeyRound className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  )}
                  <span className="flex-1 truncate font-medium">{secret.name}</span>
                  <div className="hidden shrink-0 gap-1 sm:flex">
                    {secret.tags.map((tag) => (
                      <Badge key={tag.id} variant="outline" style={{ borderColor: tag.color, color: tag.color }}>
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                  <Badge variant="secondary" className="shrink-0">
                    {SECRET_TYPE_LABELS[secret.type]}
                  </Badge>
                  <span className="hidden shrink-0 text-xs text-muted-foreground sm:inline">
                    {formatRelativeTime(secret.updated_at)}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <SecretDetailSheet
        secretId={openId}
        onClose={closeDetail}
        onEdit={() => openId && startEdit(openId)}
      />

      <SecretFormDialog
        open={formOpen}
        onOpenChange={(o) => {
          setFormOpen(o);
          if (!o) setEditSecret(null);
        }}
        secret={editSecret ? (editQuery.data ?? editSecret) : null}
        folderId={folderId}
        onSaved={(id) => router.push(`/vault?open=${id}`)}
      />
    </div>
  );
}
