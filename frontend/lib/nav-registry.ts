import {
  FileText,
  FlaskConical,
  FolderKanban,
  KeyRound,
  LayoutDashboard,
  Library,
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
  { title: "Knowledge", href: "/knowledge", icon: Library, description: "Search, tag & link notes and documents", shortcut: "K" },
  { title: "Projects", href: "/projects", icon: FolderKanban, description: "Group secrets, notes & documents by workspace", shortcut: "P" },
  { title: "Generators", href: "/generators", icon: Wand2, description: "Passwords, UUIDs, keys", shortcut: "G" },
  { title: "Crypto", href: "/crypto", icon: ShieldHalf, description: "Encrypt, hash, sign, JWT", shortcut: "C" },
  { title: "Converter", href: "/converters", icon: Repeat, description: "Text, data & document conversion", shortcut: "O" },
  { title: "Utilities", href: "/utilities", icon: Wrench, description: "QR, checksums, timezones", shortcut: "U" },
  { title: "Project Init", href: "/project-init", icon: Sparkles, description: "Generate FDK scaffolds & AI instructions" },
  { title: "Prompt Studio", href: "/prompt-studio", icon: MessageSquareText, description: "Author, version & preview LLM prompts" },
  { title: "Model Playground", href: "/model-playground", icon: FlaskConical, description: "Compare LLM provider outputs side by side" },
  { title: "Settings", href: "/settings", icon: Settings, description: "Theme, backup, about", shortcut: "," },
];
