import { cn, severityColor } from "@/lib/utils";

export function SeverityBadge({ severity }: { severity: string | null | undefined }) {
  const key = (severity || "low").toLowerCase();
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide",
        severityColor[key] || severityColor.low
      )}
    >
      {key}
    </span>
  );
}

export function Badge({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground",
        className
      )}
    >
      {children}
    </span>
  );
}
