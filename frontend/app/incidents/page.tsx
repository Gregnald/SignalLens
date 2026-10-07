"use client";

import { useEffect, useState } from "react";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { IncidentSummary } from "@/lib/types";
import { EmptyState, ErrorState, Skeleton } from "@/components/ui/states";
import { IncidentCard } from "@/components/incidents/incident-card";
import { Card, CardTitle } from "@/components/ui/card";
import { ImpactGrowthScatter } from "@/components/charts/impact-growth-scatter";

export default function IncidentRadarPage() {
  const { datasetId } = useDataset();
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .listIncidents(datasetId)
      .then(setIncidents)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load incidents"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (!datasetId) return <EmptyState title="No dataset selected" />;

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">Active Customer Incidents</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Ranked by impact score — volume, growth, severity, sentiment, reach, and confidence.
      </p>

      {loading && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} />}

      {!loading && !error && incidents.length === 0 && (
        <EmptyState
          title="No incidents yet"
          description="Incidents are generated from themes whose impact score clears the threshold. Process a dataset to populate this view."
        />
      )}

      {!loading && !error && incidents.length > 0 && (
        <>
          <Card className="mb-6">
            <CardTitle>Impact vs growth</CardTitle>
            <ImpactGrowthScatter
              data={incidents.map((i) => ({
                title: i.title,
                impact_score: i.impact_score,
                growth_percent: i.growth_percent,
                severity: i.severity,
              }))}
            />
          </Card>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {incidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
