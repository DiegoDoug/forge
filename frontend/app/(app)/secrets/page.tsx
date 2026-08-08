"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { KeyRound, Plus, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataList, DataListRow, DataListSkeleton } from "@/components/data-list";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { FilterRail } from "@/components/filter-rail";
import { PageHeader } from "@/components/page-header";
import { SearchField } from "@/components/search-field";
import { Toolbar } from "@/components/toolbar";
import { formatRelativeTime } from "@/lib/format";
import { useSecrets, secretsApi, type SecretDetail } from "@/features/secrets/api";
import { SECRET_TYPE_LABELS } from "@/features/secrets/secret-types";
import { SecretDetailSheet } from "@/features/secrets/secret-detail-sheet";
import { SecretFormDialog } from "@/features/secrets/secret-form-dialog";
import { SecretsFilters } from "@/features/secrets/secrets-filters";
import { ProjectPicker } from "@/features/projects/project-picker";

export default function SecretsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const openId = searchParams.get("open");

  const [folderId, setFolderId] = useState<string | null>(null);
  const [tagId, setTagId] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(() => searchParams.get("project_id"));
  const [query, setQuery] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editSecret, setEditSecret] = useState<SecretDetail | null>(null);

  const secretsQuery = useSecrets({
    folder_id: folderId ?? undefined,
    tag_id: tagId ?? undefined,
    project_id: projectId ?? undefined,
    q: query || undefined,
  });

  const editQuery = useQuery({
    queryKey: ["secrets", "secret", editSecret?.id, "edit"],
    queryFn: () => secretsApi.getSecret(editSecret!.id, true),
    enabled: Boolean(editSecret),
  });

  const closeDetail = () => router.push("/secrets");

  async function startEdit(id: string) {
    const detail = await secretsApi.getSecret(id, true);
    setEditSecret(detail);
    setFormOpen(true);
  }

  const secrets = useMemo(() => secretsQuery.data ?? [], [secretsQuery.data]);
  const hasActiveFilters = Boolean(folderId || tagId || projectId || query);

  function clearFilters() {
    setFolderId(null);
    setTagId(null);
    setProjectId(null);
    setQuery("");
  }

  // Deep-link from the Workbench Quick Actions panel (?new=1): open the
  // create-secret dialog immediately, then drop the param.
  const consumedNewParam = useRef(false);
  useEffect(() => {
    if (searchParams.get("new") && !consumedNewParam.current) {
      consumedNewParam.current = true;
      setEditSecret(null);
      setFormOpen(true);
      router.replace("/secrets");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div>
      <PageHeader
        title="Secrets"
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

      <Toolbar>
        <SearchField value={query} onChange={setQuery} placeholder="Search secrets…" className="max-w-sm flex-1" />
        <ProjectPicker value={projectId} onChange={setProjectId} className="w-48" />
      </Toolbar>

      <div className="flex flex-col lg:flex-row">
        <FilterRail title="Filters">
          <SecretsFilters folderId={folderId} tagId={tagId} onFolderChange={setFolderId} onTagChange={setTagId} />
        </FilterRail>

        <div className="flex-1 p-4 md:p-6">
          {secretsQuery.isLoading ? (
            <DataListSkeleton rows={4} />
          ) : secretsQuery.isError ? (
            <ErrorState description="Couldn't load your secrets." onRetry={() => secretsQuery.refetch()} />
          ) : secrets.length === 0 ? (
            hasActiveFilters ? (
              <EmptyState
                icon={KeyRound}
                title="No secrets match these filters"
                description="Try a different folder, tag, project, or search term."
                action={
                  <Button size="sm" variant="outline" onClick={clearFilters}>
                    Clear filters
                  </Button>
                }
              />
            ) : (
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
            )
          ) : (
            <DataList>
              {secrets.map((secret) => (
                <DataListRow key={secret.id} onClick={() => router.push(`/secrets?open=${secret.id}`)}>
                  {secret.favorite ? (
                    <Star className="h-3.5 w-3.5 shrink-0 fill-primary text-primary" />
                  ) : (
                    <KeyRound className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  )}
                  <span className="data-primary flex-1 truncate">{secret.name}</span>
                  <div className="hidden shrink-0 gap-1 sm:flex">
                    {secret.tags.map((tag) => (
                      <Badge key={tag.id} variant="outline" style={{ borderColor: tag.color }}>
                        <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: tag.color }} />
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                  <Badge variant="secondary" className="shrink-0">
                    {SECRET_TYPE_LABELS[secret.type]}
                  </Badge>
                  <span className="data-meta hidden shrink-0 sm:inline">{formatRelativeTime(secret.updated_at)}</span>
                </DataListRow>
              ))}
            </DataList>
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
        projectId={projectId}
        onSaved={(id) => router.push(`/secrets?open=${id}`)}
      />
    </div>
  );
}
