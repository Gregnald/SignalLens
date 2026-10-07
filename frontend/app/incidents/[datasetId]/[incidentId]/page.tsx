"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { FileText } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import type { ActionReport, IncidentDetail } from "@/lib/types";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";
import { formatPercent } from "@/lib/utils";

export default function IncidentDetailPage() {
  const params = useParams<{ datasetId: string; incidentId: string }>();
  const datasetId = Number(params.datasetId);
  const incidentId = Number(params.incidentId);

  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ActionReport | null>(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .getIncident(datasetId, incidentId)
      .then(setIncident)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load incident"))
      .finally(() => setLoading(false));
  }, [datasetId, incidentId]);

  async function handleGenerateReport() {
    setGenerating(true);
    try {
      const res = await api.generateAction(incidentId);
      setReport(res.report);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to generate report");
    } finally {
      setGenerating(false);
    }
  }

  if (loading) return <LoadingState label="Loading incident…" />;
  if (error) return <ErrorState message={error} />;
  if (!incident) return <EmptyState title="Incident not found" />;

  const segments = [
    ["Platform", incident.affected_platforms],
    ["App version", incident.affected_versions],
    ["Device", incident.affected_devices],
  ] as const;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <SeverityBadge severity={incident.severity} />
        <h1 className="mt-2 text-2xl font-semibold">{incident.title}</h1>
        {incident.summary && <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{incident.summary}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardTitle>Impact score</CardTitle>
          <CardValue>{Math.round(incident.impact_score)}</CardValue>
        </Card>
        <Card>
          <CardTitle>Growth</CardTitle>
          <CardValue className="text-critical">{formatPercent(incident.growth_percent)}</CardValue>
        </Card>
        <Card>
          <CardTitle>Rating impact</CardTitle>
          <CardValue>{incident.rating_impact ?? "—"}</CardValue>
        </Card>
        <Card>
          <CardTitle>First detected</CardTitle>
          <CardValue className="text-base">
            {incident.first_detected_at ? new Date(incident.first_detected_at).toLocaleDateString() : "—"}
          </CardValue>
        </Card>
      </div>

      <Card>
        <CardTitle>Likely driver</CardTitle>
        <p className="mt-1 text-xl font-semibold">{incident.likely_driver ?? "Insufficient evidence to identify a likely driver"}</p>
        {incident.root_cause_confidence !== null && (
          <p className="mt-1 text-sm text-muted-foreground">
            Confidence: {Math.round(incident.root_cause_confidence)}%
          </p>
        )}
        <p className="mt-2 text-xs text-muted-foreground">
          Computed from release/platform/device concentration — a likely driver, not a confirmed root cause.
        </p>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {segments.map(([label, data]) => (
          <Card key={label}>
            <CardTitle>{label}</CardTitle>
            <div className="mt-2 flex flex-col gap-1">
              {data && Object.keys(data).length > 0 ? (
                Object.entries(data).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-sm">
                    <span>{k}</span>
                    <span className="font-medium">{v}%</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No segment data</p>
              )}
            </div>
          </Card>
        ))}
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Evidence</h2>
        {incident.evidence.length === 0 ? (
          <EmptyState title="No evidence collected yet" />
        ) : (
          <div className="flex flex-col gap-2">
            {incident.evidence.map((e) => (
              <div key={e.id} className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
                <p className="mb-1 text-xs uppercase tracking-wide text-muted-foreground">
                  {e.evidence_type.replace(/_/g, " ")}
                </p>
                <p>{e.evidence_text}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recommended action</h2>
          <Button onClick={handleGenerateReport} disabled={generating}>
            <FileText className="h-4 w-4" />
            {generating ? "Generating…" : "Generate Engineering Report"}
          </Button>
        </div>

        {report && (
          <Card>
            <h3 className="text-lg font-semibold">{report.title}</h3>
            <p className="mt-2 text-sm">
              <strong>Problem: </strong>
              {report.problem}
            </p>
            <p className="mt-2 text-sm">
              <strong>Impact: </strong>
              {report.impact}
            </p>
            <p className="mt-2 text-sm">
              <strong>Affected users: </strong>
              {report.affected_users}
            </p>
            <p className="mt-2 text-sm">
              <strong>Likely driver: </strong>
              {report.likely_driver}
            </p>
            <p className="mt-2 text-sm">
              <strong>Evidence summary: </strong>
              {report.representative_evidence_summary}
            </p>
            <div className="mt-3 flex gap-4 text-sm">
              <span>
                <strong>Severity:</strong> {report.severity}
              </span>
              <span>
                <strong>Owner:</strong> {report.recommended_owner}
              </span>
              <span>
                <strong>Priority:</strong> {report.priority}
              </span>
            </div>
            <div className="mt-3">
              <strong className="text-sm">Next steps:</strong>
              <ul className="mt-1 list-disc pl-5 text-sm">
                {report.next_steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>
          </Card>
        )}
      </section>
    </div>
  );
}
