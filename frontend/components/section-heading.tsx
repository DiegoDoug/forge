import { cn } from "@/lib/utils";

// Applies the Swiss `.label-structural` register (globals.css). Replaces the
// hand-written "text-sm font-semibold tracking-wide uppercase" pattern
// duplicated in Converter and Project Init.
export function SectionHeading({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <h2 className={cn("label-structural", className)}>{children}</h2>;
}
