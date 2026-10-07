"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ThemeTrendPoint } from "@/lib/types";

export function TrendChart({ data }: { data: ThemeTrendPoint[] }) {
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No trend data available.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border))" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="rgb(var(--muted-foreground))" />
        <YAxis tick={{ fontSize: 11 }} stroke="rgb(var(--muted-foreground))" allowDecimals={false} />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgb(var(--card))",
            border: "1px solid rgb(var(--border))",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Line type="monotone" dataKey="volume" stroke="rgb(var(--primary))" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
