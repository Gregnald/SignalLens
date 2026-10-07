"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { CHART_AXIS, CHART_GRID, TOOLTIP_STYLE, TOOLTIP_LABEL_STYLE } from "./chart-colors";

/** Ordered 1-5 star distribution — one series, sequential blue, ordered x-axis. */
export function RatingDistributionChart({ distribution }: { distribution: Record<string, number> }) {
  const data = [1, 2, 3, 4, 5].map((star) => ({
    star: `${star}★`,
    count: distribution[String(star)] ?? 0,
  }));
  const total = data.reduce((sum, d) => sum + d.count, 0);

  if (total === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No ratings yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke={CHART_GRID} />
        <XAxis dataKey="star" tick={{ fontSize: 11 }} stroke={CHART_AXIS} />
        <YAxis tick={{ fontSize: 11 }} stroke={CHART_AXIS} allowDecimals={false} />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={TOOLTIP_LABEL_STYLE}
          formatter={(value: number) => [value.toLocaleString(), "Reviews"]}
          cursor={{ fill: "rgb(var(--muted))" }}
        />
        <Bar dataKey="count" fill="var(--chart-1)" radius={[4, 4, 0, 0]} maxBarSize={48} />
      </BarChart>
    </ResponsiveContainer>
  );
}
