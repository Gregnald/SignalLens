"use client";

import { useEffect, useState } from "react";
import { ShieldAlert } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { IntegrityReport } from "@/lib/types";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";

export default function IntegrityPage() {
  const { datasetId } = useDataset();
  const [report, setReport] = useState<IntegrityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .getIntegrity(datasetId)
      .then(setReport)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load integrity report"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (!datasetId) return <EmptyState title="No dataset selected" />;
  if (loading) return <LoadingState label="Scanning for anomalous feedback patterns…" />;
  if (error) return <ErrorState message={error} />;
  if (!report) return <EmptyState title="No data yet" />;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-6 w-6" />
        <h1 className="text-2xl font-semibold">Feedback Integrity</h1>
      </div>
      <p className="-mt-6 max-w-2xl text-sm text-muted-foreground">
        These are anomalous feedback patterns, not confirmed fake reviews — near-duplicate text,
        unusually dense submission bursts, and rating/text contradictions.
      </p>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardTitle>Total reviews</CardTitle>
          <CardValue>{report.total_reviews}</CardValue>
        </Card>
        <Card>
          <CardTitle>Flagged %</CardTitle>
          <CardValue className="text-critical">{report.flagged_percent}%</CardValue>
        </Card>
        <Card>
          <CardTitle>Duplicate groups</CardTitle>
          <CardValue>{report.duplicate_groups.length}</CardValue>
        </Card>
        <Card>
          <CardTitle>Suspicious bursts</CardTitle>
          <CardValue>{report.bursts.length}</CardValue>
        </Card>
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Suspicious feedback bursts</h2>
        {report.bursts.length === 0 ? (
          <EmptyState title="No suspicious bursts detected" />
        ) : (
          <div className="flex flex-col gap-3">
            {report.bursts.map((burst, i) => (
              <Card key={i}>
                <p className="text-sm font-medium text-critical">⚠ Suspicious feedback burst</p>
                <p className="mt-1 text-sm">
                  {burst.review_count} near-duplicate reviews between {burst.window_start} and{" "}
                  {burst.window_end}
                  {burst.dominant_rating !== null && `, dominant rating ${burst.dominant_rating}★`}
                </p>
                <div className="mt-2 flex flex-col gap-1 text-xs text-muted-foreground">
                  {burst.sample_texts.slice(0, 3).map((t, j) => (
                    <p key={j}>&ldquo;{t}&rdquo;</p>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Near-duplicate groups</h2>
        {report.duplicate_groups.length === 0 ? (
          <EmptyState title="No near-duplicate groups detected" />
        ) : (
          <div className="flex flex-col gap-3">
            {report.duplicate_groups.map((group) => (
              <Card key={group.duplicate_group_id}>
                <p className="text-sm font-medium">
                  {group.review_count} reviews, ≥{Math.round(group.avg_similarity * 100)}% semantic similarity
                </p>
                <div className="mt-2 flex flex-col gap-1 text-xs text-muted-foreground">
                  {group.sample_texts.slice(0, 3).map((t, j) => (
                    <p key={j}>&ldquo;{t}&rdquo;</p>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Rating / text conflicts</h2>
        {report.rating_text_conflicts.length === 0 ? (
          <EmptyState title="No rating/text conflicts detected" />
        ) : (
          <div className="flex flex-col gap-2">
            {report.rating_text_conflicts.map((c) => (
              <div key={c.review_id} className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
                <p className="mb-1 text-xs text-muted-foreground">Rating: {c.rating}★</p>
                <p>{c.text}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
