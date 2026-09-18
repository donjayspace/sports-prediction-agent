"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface ProbabilityChartProps {
  stat: { home: number; draw: number; away: number } | null;
  llm: { home: number; draw: number; away: number } | null;
  final: { home: number; draw: number; away: number };
}

interface ChartRow {
  outcome: string;
  Statistical: number;
  LLM: number;
  Final: number;
}

function toPercent(v: number | undefined): number {
  return v === undefined ? 0 : Math.round(v * 1000) / 10;
}

export function ProbabilityChart({ stat, llm, final }: ProbabilityChartProps): JSX.Element {
  const data: ChartRow[] = [
    {
      outcome: "Home",
      Statistical: toPercent(stat?.home),
      LLM: toPercent(llm?.home),
      Final: toPercent(final.home),
    },
    {
      outcome: "Draw",
      Statistical: toPercent(stat?.draw),
      LLM: toPercent(llm?.draw),
      Final: toPercent(final.draw),
    },
    {
      outcome: "Away",
      Statistical: toPercent(stat?.away),
      LLM: toPercent(llm?.away),
      Final: toPercent(final.away),
    },
  ];

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-4 text-xl font-semibold">Probability breakdown</h2>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="outcome" stroke="#94a3b8" />
            <YAxis
              stroke="#94a3b8"
              domain={[0, 100]}
              tickFormatter={(v: number) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid #1e293b",
                borderRadius: 8,
              }}
              formatter={(value: number) => `${value.toFixed(1)}%`}
            />
            <Legend />
            <Bar dataKey="Statistical" fill="#475569" radius={[4, 4, 0, 0]} />
            <Bar dataKey="LLM" fill="#7c3aed" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Final" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
