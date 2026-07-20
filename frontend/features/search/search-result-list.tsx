import Link from "next/link";
import { FileText, KeyRound, StickyNote, type LucideIcon } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import type { SearchResults } from "./api";

export function SearchResultList({ results, query }: { results: SearchResults; query: string }) {
  const hasResults = results.secrets.length > 0 || results.notes.length > 0 || results.documents.length > 0;

  if (!hasResults) {
    return <EmptyState icon={FileText} title={`No matches for "${query}"`} />;
  }

  return (
    <div className="flex flex-col gap-6">
      {results.secrets.length > 0 ? (
        <ResultGroup title="Secrets" icon={KeyRound}>
          {results.secrets.map((s) => (
            <ResultRow key={s.id} href={`/secrets?open=${s.id}`} icon={KeyRound} label={s.name} />
          ))}
        </ResultGroup>
      ) : null}

      {results.notes.length > 0 ? (
        <ResultGroup title="Notes" icon={StickyNote}>
          {results.notes.map((n) => (
            <ResultRow key={n.id} href={`/notes?open=${n.id}`} icon={StickyNote} label={n.title} sublabel={n.excerpt} />
          ))}
        </ResultGroup>
      ) : null}

      {results.documents.length > 0 ? (
        <ResultGroup title="Documents" icon={FileText}>
          {results.documents.map((d) => (
            <ResultRow key={d.id} href={`/documents?open=${d.id}`} icon={FileText} label={d.title} />
          ))}
        </ResultGroup>
      ) : null}
    </div>
  );
}

function ResultGroup({ title, icon: Icon, children }: { title: string; icon: LucideIcon; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="mb-2 flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Icon className="h-4 w-4" /> {title}
      </h2>
      <div className="overflow-hidden rounded-xl border border-border">{children}</div>
    </div>
  );
}

function ResultRow({
  href,
  icon: Icon,
  label,
  sublabel,
}: {
  href: string;
  icon: LucideIcon;
  label: string;
  sublabel?: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 border-t border-border px-4 py-3 text-sm first:border-t-0 hover:bg-accent/40"
    >
      <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{label}</p>
        {sublabel ? <p className="truncate text-xs text-muted-foreground">{sublabel}</p> : null}
      </div>
    </Link>
  );
}
