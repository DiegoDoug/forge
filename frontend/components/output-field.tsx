import { CopyButton } from "@/components/copy-button";
import { cn } from "@/lib/utils";

export function OutputField({
  value,
  placeholder = "Output will appear here",
  className,
  mono = true,
}: {
  value: string;
  placeholder?: string;
  className?: string;
  mono?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-1 rounded-lg border border-border bg-muted/40 px-3 py-2",
        className,
      )}
    >
      <code
        className={cn(
          "min-w-0 flex-1 truncate text-sm",
          mono && "font-mono",
          !value && "text-muted-foreground",
        )}
      >
        {value || placeholder}
      </code>
      {value ? <CopyButton value={value} /> : null}
    </div>
  );
}
