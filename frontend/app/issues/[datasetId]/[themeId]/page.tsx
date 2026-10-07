"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { api, ApiError } from "@/lib/api";
import type { ThemeDetail } from "@/lib/types";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";
import { TrendChart } from "@/components/charts/trend-chart";
import { formatPercent } from "@/lib/utils";

export default function ThemeDetailPage() {
  const params = useParams<{ datasetId: string; themeId: string }>();
  const datasetId = Number(params.datasetId);
  const themeId = Number(params.themeId);

  const [theme, setTheme] = useState<ThemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .getTheme(datasetId, themeId)
      .then(setTheme)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load theme"))
      .finally(() => setLoading(false));
  }, [datasetId, themeId]);

  if (loading) return <LoadingState label="Loading theme…" />;
  if (error) return <ErrorState message={error} />;
  if (!theme) return <EmptyState title="Theme not found" />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <SeverityBadge severity={theme.severity} />
        <h1 className="mt-2 text-2xl font-semibold">{theme.name}</h1>
        {theme.description && <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{theme.description}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardTitle>Volume</CardTitle>
          <CardValue>{theme.volume}</CardValue>
        </Card>
        <Card>
          <CardTitle>Growth</CardTitle>
          <CardValue>{formatPercent(theme.growth_percent)}</CardValue>
        </Card>
        <Card>
          <CardTitle>Negative %</CardTitle>
          <CardValue>{theme.negative_percent ?? "—"}%</CardValue>
        </Card>
        <Card>
          <CardTitle>Impact score</CardTitle>
          <CardValue>{theme.impact_score !== null ? Math.round(theme.impact_score) : "—"}</CardValue>
        </Card>
      </div>

      <Card>
        <CardTitle>Volume over time</CardTitle>
        <TrendChart data={theme.trend} />
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {Object.entries(theme.affected_segments).map(([field, values]) => (
          <Card key={field}>
            <CardTitle className="capitalize">{field.replace("_", " ")}</CardTitle>
            <div className="mt-2 flex flex-col gap-1">
              {Object.keys(values).length === 0 ? (
                <p className="text-sm text-muted-foreground">No data</p>
              ) : (
                Object.entries(values)
                  .slice(0, 5)
                  .map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm">
                      <span>{k}</span>
                      <span className="font-medium">{v}%</span>
                    </div>
                  ))
              )}
            </div>
          </Card>
        ))}
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Representative reviews</h2>
        {theme.representative_reviews.length === 0 ? (
          <EmptyState title="No representative reviews yet" />
        ) : (
          <div className="flex flex-col gap-2">
            {theme.representative_reviews.map((text, i) => (
              <div key={i} className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
                {text}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
