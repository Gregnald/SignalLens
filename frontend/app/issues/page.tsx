"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { Theme } from "@/lib/types";
import { SeverityBadge } from "@/components/ui/badge";
import { EmptyState, ErrorState, Skeleton } from "@/components/ui/states";
import { formatPercent } from "@/lib/utils";

const SEVERITIES = ["critical", "high", "medium", "low"];

export default function IssueExplorerPage() {
  const { datasetId } = useDataset();
  const [themes, setThemes] = useState<Theme[]>([]);
  const [severity, setSeverity] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .listThemes(datasetId, severity ? { severity } : undefined)
      .then(setThemes)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load issues"))
      .finally(() => setLoading(false));
  }, [datasetId, severity]);

  if (!datasetId) return <EmptyState title="No dataset selected" />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Issue Explorer</h1>
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
        >
          <option value="">All severities</option>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="flex flex-col gap-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} />}

      {!loading && !error && themes.length === 0 && (
        <EmptyState title="No themes found" description="Process a dataset or widen your filter." />
      )}

      {!loading && !error && themes.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-2 text-left">Theme</th>
                <th className="px-4 py-2 text-left">Severity</th>
                <th className="px-4 py-2 text-right">Volume</th>
                <th className="px-4 py-2 text-right">Growth</th>
                <th className="px-4 py-2 text-right">Negative %</th>
                <th className="px-4 py-2 text-right">Impact</th>
              </tr>
            </thead>
            <tbody>
              {themes.map((theme) => (
                <tr key={theme.id} className="border-t border-border hover:bg-muted">
                  <td className="px-4 py-3">
                    <Link href={`/issues/${datasetId}/${theme.id}`} className="font-medium hover:underline">
                      {theme.name}
                      {theme.is_emerging && (
                        <span className="ml-2 rounded-full bg-critical/10 px-2 py-0.5 text-xs text-critical">
                          NEW
                        </span>
                      )}
                    </Link>
                    <p className="text-xs text-muted-foreground">{theme.category}</p>
                  </td>
                  <td className="px-4 py-3">
                    <SeverityBadge severity={theme.severity} />
                  </td>
                  <td className="px-4 py-3 text-right">{theme.volume}</td>
                  <td className="px-4 py-3 text-right">{formatPercent(theme.growth_percent)}</td>
                  <td className="px-4 py-3 text-right">{theme.negative_percent ?? "—"}%</td>
                  <td className="px-4 py-3 text-right font-semibold">
                    {theme.impact_score !== null ? Math.round(theme.impact_score) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
