"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";
import { FileText, KeyRound, Lock, StickyNote } from "lucide-react";

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

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

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

          {results.data &&
          (results.data.secrets.length > 0 || results.data.notes.length > 0 || results.data.documents.length > 0) ? (
            <>
              <CommandSeparator />
              {results.data.secrets.length > 0 ? (
                <CommandGroup heading="Vault">
                  {results.data.secrets.map((s) => (
                    <CommandItem key={s.id} value={`secret-${s.id}`} onSelect={() => go(`/vault?open=${s.id}`)}>
                      <KeyRound className="h-4 w-4" />
                      <span>{s.name}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              ) : null}
              {results.data.notes.length > 0 ? (
                <CommandGroup heading="Notes">
                  {results.data.notes.map((n) => (
                    <CommandItem key={n.id} value={`note-${n.id}`} onSelect={() => go(`/notes?open=${n.id}`)}>
                      <StickyNote className="h-4 w-4" />
                      <span>{n.title}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              ) : null}
              {results.data.documents.length > 0 ? (
                <CommandGroup heading="Documents">
                  {results.data.documents.map((d) => (
                    <CommandItem key={d.id} value={`document-${d.id}`} onSelect={() => go(`/documents?open=${d.id}`)}>
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
