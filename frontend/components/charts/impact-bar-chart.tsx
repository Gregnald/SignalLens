"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { CHART_AXIS, CHART_GRID, TOOLTIP_STYLE, TOOLTIP_LABEL_STYLE, STATUS_COLOR } from "./chart-colors";

interface ImpactBarDatum {
  name: string;
  impact_score: number;
  severity: string;
}

/** Single-series magnitude comparison across named themes — sequential/status hue,
 * never a rainbow of categorical colors for what is really one measure per bar.
 * Severity still carries meaning here, so each bar is tinted by its status color
 * (reserved channel, not a generic categorical fill) rather than one flat hue.
 */
export function ImpactBarChart({ data }: { data: ImpactBarDatum[] }) {
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No issues scored yet.</p>;
  }

  const chartData = [...data].reverse(); // Recharts horizontal bars render bottom-up

  return (
    <ResponsiveContainer width="100%" height={Math.max(160, chartData.length * 36)}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke={CHART_GRID} />
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} stroke={CHART_AXIS} />
        <YAxis
          type="category"
          dataKey="name"
          width={160}
          tick={{ fontSize: 11 }}
          stroke={CHART_AXIS}
          tickFormatter={(value: string) => (value.length > 28 ? `${value.slice(0, 27)}…` : value)}
        />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={TOOLTIP_LABEL_STYLE}
          formatter={(value: number) => [Math.round(value), "Impact score"]}
          cursor={{ fill: "rgb(var(--muted))" }}
        />
        <Bar dataKey="impact_score" radius={[0, 4, 4, 0]} maxBarSize={24}>
          {chartData.map((d, i) => (
            <Cell key={i} fill={STATUS_COLOR[d.severity] ?? "var(--chart-1)"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
