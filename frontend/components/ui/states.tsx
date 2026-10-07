import { AlertTriangle, Inbox, Loader2 } from "lucide-react";

export function Skeleton({ className = "h-24 w-full" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-muted ${className}`} />;
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-16 text-center text-muted-foreground">
      <Inbox className="h-6 w-6" />
      <p className="text-sm font-medium">{title}</p>
      {description && <p className="max-w-sm text-xs">{description}</p>}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-critical/30 bg-critical/5 py-16 text-center text-critical">
      <AlertTriangle className="h-6 w-6" />
      <p className="text-sm font-medium">Something went wrong</p>
      <p className="max-w-sm text-xs text-critical/80">{message}</p>
    </div>
  );
}
