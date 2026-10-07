"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { TrendingUp } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { DashboardData } from "@/lib/types";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import { EmptyState, ErrorState, LoadingState, Skeleton } from "@/components/ui/states";
import { formatNumber, formatPercent } from "@/lib/utils";
import { IncidentCard } from "@/components/incidents/incident-card";
import { SentimentBar } from "@/components/charts/sentiment-bar";
import { ImpactBarChart } from "@/components/charts/impact-bar-chart";

export default function DashboardPage() {
  const { datasetId } = useDataset();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .getDashboard(datasetId)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (!datasetId) {
    return (
      <EmptyState
        title="Catalog is still loading"
        description="The Flipkart marketplace catalog is being seeded — this should only take a moment on first startup."
      />
    );
  }

  if (loading) {
    return (
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
    );
  }

  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState title="No data yet" />;

  return (
    <div className="flex flex-col gap-8">
      <section className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <Card>
          <CardTitle>Total reviews</CardTitle>
          <CardValue>{formatNumber(data.total_reviews)}</CardValue>
        </Card>
        <Card>
          <CardTitle>Critical incidents</CardTitle>
          <CardValue className="text-critical">{data.critical_incidents}</CardValue>
        </Card>
        <Card>
          <CardTitle>Emerging issues</CardTitle>
          <CardValue>{data.emerging_issues}</CardValue>
        </Card>
        <Card>
          <CardTitle>Average rating</CardTitle>
          <CardValue>{data.average_rating ?? "—"}</CardValue>
        </Card>
        <Card>
          <CardTitle>Negative feedback</CardTitle>
          <CardValue>{data.negative_percent}%</CardValue>
        </Card>
        <Card>
          <CardTitle>Complaint increase</CardTitle>
          <CardValue>
            {data.complaint_increase_multiplier ? `${data.complaint_increase_multiplier}×` : "—"}
          </CardValue>
        </Card>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Sentiment breakdown</h2>
        <Card>
          <SentimentBar
            positive={data.sentiment_breakdown.positive ?? 0}
            neutral={data.sentiment_breakdown.neutral ?? 0}
            negative={data.sentiment_breakdown.negative ?? 0}
          />
        </Card>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
          <TrendingUp className="h-5 w-5" /> What Changed?
        </h2>
        {data.what_changed.length === 0 ? (
          <EmptyState title="No significant changes detected yet." />
        ) : (
          <div className="flex flex-col gap-2">
            {data.what_changed.map((item) => (
              <Link
                key={item.theme_id}
                href={`/issues/${data.dataset_id}/${item.theme_id}`}
                className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3 hover:bg-muted"
              >
                <div className="flex items-center gap-3">
                  <SeverityBadge severity={item.severity} />
                  <span className="font-medium">{item.theme_name}</span>
                </div>
                <span className="font-semibold text-critical">{formatPercent(item.growth_percent)}</span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Top issues by impact</h2>
        {data.top_issues.length === 0 ? (
          <EmptyState title="No themes discovered yet." description="Process a dataset to see issues here." />
        ) : (
          <>
            <Card className="mb-3">
              <ImpactBarChart
                data={data.top_issues.map((i) => ({
                  name: i.theme_name,
                  impact_score: i.impact_score,
                  severity: i.severity,
                }))}
              />
            </Card>
            <div className="flex flex-col gap-2">
            {data.top_issues.map((item, idx) => (
              <Link
                key={item.theme_id}
                href={`/issues/${data.dataset_id}/${item.theme_id}`}
                className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3 hover:bg-muted"
              >
                <div className="flex items-center gap-3">
                  <span className="w-5 text-sm text-muted-foreground">{idx + 1}</span>
                  <SeverityBadge severity={item.severity} />
                  <span className="font-medium">{item.theme_name}</span>
                </div>
                <span className="font-semibold">{Math.round(item.impact_score)}</span>
              </Link>
            ))}
            </div>
          </>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Recent incidents</h2>
        {data.recent_incidents.length === 0 ? (
          <EmptyState title="No incidents yet." />
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data.recent_incidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
