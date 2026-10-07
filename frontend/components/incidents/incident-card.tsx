import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import type { IncidentSummary } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import { formatPercent } from "@/lib/utils";

export function IncidentCard({ incident }: { incident: IncidentSummary }) {
  return (
    <Link href={`/incidents/${incident.dataset_id}/${incident.id}`}>
      <Card className="transition-shadow hover:shadow-md">
        <div className="flex items-start justify-between">
          <div>
            <SeverityBadge severity={incident.severity} />
            <h3 className="mt-2 text-lg font-semibold">{incident.title}</h3>
          </div>
          <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-xs text-muted-foreground">Impact</p>
            <p className="font-semibold">{Math.round(incident.impact_score)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Growth</p>
            <p className="font-semibold">{formatPercent(incident.growth_percent)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Confidence</p>
            <p className="font-semibold">
              {incident.root_cause_confidence !== null
                ? `${Math.round(incident.root_cause_confidence)}%`
                : "—"}
            </p>
          </div>
        </div>

        {incident.likely_driver && (
          <p className="mt-3 text-xs text-muted-foreground">
            Likely driver: <span className="font-medium text-foreground">{incident.likely_driver}</span>
          </p>
        )}
      </Card>
    </Link>
  );
}
