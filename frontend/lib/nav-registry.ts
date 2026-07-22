import {
  FileInput,
  FileText,
  KeyRound,
  LayoutDashboard,
  MessageSquareText,
  Settings,
  ShieldHalf,
  Sparkles,
  StickyNote,
  Repeat,
  Wand2,
  Wrench,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  description: string;
  shortcut?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { title: "Workbench", href: "/", icon: LayoutDashboard, description: "Pinned tools & recent activity", shortcut: "D" },
  { title: "Secrets", href: "/secrets", icon: KeyRound, description: "Encrypted secrets", shortcut: "V" },
  { title: "Notes", href: "/notes", icon: StickyNote, description: "Sticky note board", shortcut: "N" },
  { title: "Documents", href: "/documents", icon: FileText, description: "Rich text editor, history & export" },
  { title: "Generators", href: "/generators", icon: Wand2, description: "Passwords, UUIDs, keys", shortcut: "G" },
  { title: "Crypto", href: "/crypto", icon: ShieldHalf, description: "Encrypt, hash, sign, JWT", shortcut: "C" },
  { title: "Converters", href: "/converters", icon: Repeat, description: "JSON, YAML, regex, diff", shortcut: "O" },
  { title: "Utilities", href: "/utilities", icon: Wrench, description: "QR, checksums, timezones", shortcut: "U" },
  { title: "Ingest", href: "/ingest", icon: FileInput, description: "Documents → Markdown", shortcut: "I" },
  { title: "Project Init", href: "/project-init", icon: Sparkles, description: "Generate FDK scaffolds & AI instructions" },
  { title: "Prompt Studio", href: "/prompt-studio", icon: MessageSquareText, description: "Author, version & preview LLM prompts" },
  { title: "Settings", href: "/settings", icon: Settings, description: "Theme, backup, about", shortcut: "," },
];
