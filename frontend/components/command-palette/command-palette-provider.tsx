"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";
import { FileText, KeyRound, Lock, SearchIcon, StickyNote } from "lucide-react";

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import { NAV_ITEMS } from "@/lib/nav-registry";
import { authApi } from "@/features/auth/api";
import { searchApi } from "@/features/search/api";

interface CommandPaletteContextValue {
  openPalette: () => void;
}

const CommandPaletteContext = createContext<CommandPaletteContextValue | null>(null);

export function useCommandPalette() {
  const ctx = useContext(CommandPaletteContext);
  if (!ctx) throw new Error("useCommandPalette must be used within CommandPaletteProvider");
  return ctx;
}

export function CommandPaletteProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();

  // ⌘K/Ctrl+K toggles the palette from anywhere, unchanged. While the
  // palette is open, ⌘/Ctrl + one of the eight NAV_ITEMS[].shortcut letters
  // jumps straight to that destination — the palette already renders these
  // via <CommandShortcut> but nothing bound them pre-Phase-09 (00_AUDIT.md
  // §4.4). Gated on a modifier key so it never fights with typing an actual
  // search query into the focused input (e.g. "Documents" starts with "D").
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (!(e.metaKey || e.ctrlKey)) return;
      const key = e.key.toLowerCase();

      if (!open) {
        if (key === "k") {
          e.preventDefault();
          setOpen(true);
        }
        return;
      }

      // While open, destination shortcuts are checked before the generic
      // close-toggle. Knowledge's own advertised shortcut is "K" - the same
      // key that opens the palette - so without this ordering, Ctrl/Cmd+K
      // while open would always just close the palette and Knowledge's
      // shortcut would be permanently unreachable (found during T28's
      // regression pass; not something a prior task had verified, since the
      // one collision that mattered is exactly the toggle key itself).
      const item = NAV_ITEMS.find((i) => i.shortcut?.toLowerCase() === key);
      if (item) {
        e.preventDefault();
        setOpen(false);
        setQuery("");
        router.push(item.href);
        return;
      }

      if (key === "k") {
        e.preventDefault();
        setOpen(false);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, router]);

  const results = useQuery({
    queryKey: ["command-search", query],
    queryFn: () => searchApi.search(query),
    enabled: open && query.trim().length > 1,
  });

  function go(href: string) {
    setOpen(false);
    setQuery("");
    router.push(href);
  }

  async function lock() {
    setOpen(false);
    await authApi.lock();
    router.replace("/unlock");
  }

  return (
    <CommandPaletteContext.Provider value={{ openPalette: () => setOpen(true) }}>
      {children}
      <CommandDialog open={open} onOpenChange={setOpen} title="Command palette" description="Search Forge">
        <CommandInput placeholder="Search tools, secrets, notes, documents…" value={query} onValueChange={setQuery} />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>

          <CommandGroup heading="Navigate">
            {NAV_ITEMS.map((item) => (
              <CommandItem key={item.href} value={`${item.title} ${item.description}`} onSelect={() => go(item.href)}>
                <item.icon className="h-4 w-4" />
                <span>{item.title}</span>
                {item.shortcut ? <CommandShortcut>{item.shortcut}</CommandShortcut> : null}
              </CommandItem>
            ))}
          </CommandGroup>

          {query.trim().length > 1 ? (
            <>
              <CommandSeparator />
              <CommandGroup heading="Search">
                <CommandItem
                  value={`view-all-results ${query}`}
                  onSelect={() => go(`/search?q=${encodeURIComponent(query.trim())}`)}
                >
                  <SearchIcon className="h-4 w-4" />
                  <span>View all results for &ldquo;{query.trim()}&rdquo;</span>
                </CommandItem>
              </CommandGroup>
            </>
          ) : null}

          {results.data &&
          (results.data.secrets.length > 0 || results.data.notes.length > 0 || results.data.documents.length > 0) ? (
            <>
              <CommandSeparator />
              {results.data.secrets.length > 0 ? (
                <CommandGroup heading="Secrets">
                  {results.data.secrets.map((s) => (
                    // value must contain the searchable text (not just the id) —
                    // cmdk fuzzy-filters items against `value` against the typed
                    // query itself, so an id-only value silently hid every
                    // result regardless of what the backend returned. Found and
                    // fixed in Phase 09 T4 while verifying "View all results".
                    <CommandItem key={s.id} value={`secret-${s.id} ${s.name}`} onSelect={() => go(`/secrets?open=${s.id}`)}>
                      <KeyRound className="h-4 w-4" />
                      <span>{s.name}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              ) : null}
              {results.data.notes.length > 0 ? (
                <CommandGroup heading="Notes">
                  {results.data.notes.map((n) => (
                    <CommandItem key={n.id} value={`note-${n.id} ${n.title}`} onSelect={() => go(`/notes?open=${n.id}`)}>
                      <StickyNote className="h-4 w-4" />
                      <span>{n.title}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              ) : null}
              {results.data.documents.length > 0 ? (
                <CommandGroup heading="Documents">
                  {results.data.documents.map((d) => (
                    <CommandItem key={d.id} value={`document-${d.id} ${d.title}`} onSelect={() => go(`/documents?open=${d.id}`)}>
                      <FileText className="h-4 w-4" />
                      <span>{d.title}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              ) : null}
            </>
          ) : null}

          <CommandSeparator />
          <CommandGroup heading="Session">
            <CommandItem value="lock forge" onSelect={lock}>
              <Lock className="h-4 w-4" />
              <span>Lock Forge</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </CommandPaletteContext.Provider>
  );
}
