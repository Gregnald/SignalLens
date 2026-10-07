"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertOctagon,
  Gauge,
  Layers,
  MessageCircleQuestion,
  MessageSquareText,
  ShieldAlert,
  ShoppingBag,
} from "lucide-react";

import { api } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import { cn } from "@/lib/utils";
import type { Dataset } from "@/lib/types";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: Gauge },
  { href: "/categories", label: "Product Catalog", icon: ShoppingBag },
  { href: "/incidents", label: "Incident Radar", icon: AlertOctagon },
  { href: "/issues", label: "Issue Explorer", icon: Layers },
  { href: "/reviews", label: "Review Explorer", icon: MessageSquareText },
  { href: "/integrity", label: "Feedback Integrity", icon: ShieldAlert },
  { href: "/investigator", label: "AI Investigator", icon: MessageCircleQuestion },
];

const STATUS_LABEL: Record<string, string> = {
  uploaded: "Queued",
  processing: "Processing…",
  processed: "Ready",
  failed: "Failed",
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { datasetId, setDatasetId } = useDataset();
  const [dataset, setDataset] = useState<Dataset | null>(null);

  useEffect(() => {
    api
      .listDatasets()
      .then((list) => {
        if (list.length > 0) {
          setDataset(list[0]);
          if (!datasetId) setDatasetId(list[0].id);
        }
      })
      .catch(() => setDataset(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (pathname === "/login") return <>{children}</>;

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 flex-col border-r border-border bg-card px-4 py-6">
        <div className="mb-8 px-2">
          <p className="text-lg font-semibold tracking-tight">SignalLens</p>
          <p className="text-xs text-muted-foreground">Flipkart Enterprise Intelligence</p>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
                pathname.startsWith(href) && "bg-muted text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>

        {dataset && (
          <div className="rounded-lg border border-border px-3 py-2 text-xs text-muted-foreground">
            <p className="font-medium text-foreground">{dataset.name}</p>
            <p>
              {dataset.total_reviews.toLocaleString()} reviews ·{" "}
              {STATUS_LABEL[dataset.status] ?? dataset.status}
            </p>
          </div>
        )}
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border bg-card px-6 py-3">
          <span className="text-sm font-medium">
            {dataset ? dataset.name : "Loading catalog…"}
          </span>
          <span className="text-xs text-muted-foreground">
            Evidence-Backed Customer Incident Intelligence
          </span>
        </header>

        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
