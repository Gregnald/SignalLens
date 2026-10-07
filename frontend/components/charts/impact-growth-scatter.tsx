"use client";

import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

import { CHART_AXIS, CHART_GRID, STATUS_COLOR, TOOLTIP_STYLE, TOOLTIP_LABEL_STYLE } from "./chart-colors";

interface IncidentPoint {
  title: string;
  impact_score: number;
  growth_percent: number | null;
  severity: string;
}

const SEVERITY_ORDER = ["critical", "high", "medium", "low"] as const;

/** Impact vs growth, one dot per incident, colored by severity (the status channel —
 * 4 distinct, purpose-built steps, not a generic categorical palette). Lets a reader
 * spot the "high impact + high growth" quadrant at a glance instead of scanning cards.
 */
export function ImpactGrowthScatter({ data }: { data: IncidentPoint[] }) {
  const points = data.filter((d) => d.growth_percent !== null);
  if (points.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">Not enough data to plot yet.</p>;
  }

  const bySeverity = SEVERITY_ORDER.map((sev) => ({
    severity: sev,
    points: points.filter((p) => p.severity === sev),
  })).filter((g) => g.points.length > 0);

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ScatterChart margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid stroke={CHART_GRID} />
        <XAxis
          type="number"
          dataKey="impact_score"
          name="Impact score"
          domain={[0, 100]}
          tick={{ fontSize: 11 }}
          stroke={CHART_AXIS}
          label={{ value: "Impact score", position: "insideBottom", offset: -4, fontSize: 11, fill: CHART_AXIS }}
        />
        <YAxis
          type="number"
          dataKey="growth_percent"
          name="Growth %"
          tick={{ fontSize: 11 }}
          stroke={CHART_AXIS}
          label={{ value: "Growth %", angle: -90, position: "insideLeft", fontSize: 11, fill: CHART_AXIS }}
        />
        <ZAxis range={[80, 80]} />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={TOOLTIP_LABEL_STYLE}
          cursor={{ strokeDasharray: "3 3", stroke: CHART_AXIS }}
          formatter={(value: number, name: string) => [
            name === "Growth %" ? `${value.toFixed(0)}%` : Math.round(value),
            name,
          ]}
          labelFormatter={() => ""}
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const p = payload[0].payload as IncidentPoint;
            return (
              <div style={TOOLTIP_STYLE} className="px-3 py-2">
                <p className="mb-1 text-xs font-semibold">{p.title}</p>
                <p className="text-xs" style={TOOLTIP_LABEL_STYLE}>
                  Impact <span className="font-semibold text-foreground">{Math.round(p.impact_score)}</span>
                  {"  ·  "}
                  Growth <span className="font-semibold text-foreground">{p.growth_percent?.toFixed(0)}%</span>
                </p>
              </div>
            );
          }}
        />
        <Legend
          formatter={(value: string) => <span className="text-xs capitalize text-muted-foreground">{value}</span>}
        />
        {bySeverity.map((g) => (
          <Scatter key={g.severity} name={g.severity} data={g.points} fill={STATUS_COLOR[g.severity]} />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}
