"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface CalibrationPoint {
  bin: number;
  predicted: number;
  observed: number;
  count: number;
}

export interface CalibrationChartProps {
  points: CalibrationPoint[];
}

interface ChartRow {
  label: string;
  Predicted: number;
  Observed: number;
  Perfect: number;
}

export function CalibrationChart({ points }: CalibrationChartProps): JSX.Element {
  const data: ChartRow[] = points.map((p) => {
    const midpoint = (p.bin * 10 + 5) / 100;
    return {
      label: `${p.bin * 10}–${p.bin * 10 + 10}%`,
      Predicted: Math.round(p.predicted * 1000) / 10,
      Observed: Math.round(p.observed * 1000) / 10,
      Perfect: Math.round(midpoint * 1000) / 10,
    };
  });

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-4 text-xl font-semibold">Reliability diagram</h2>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="label" stroke="#94a3b8" />
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
            <Line
              type="monotone"
              dataKey="Perfect"
              stroke="#334155"
              strokeDasharray="4 4"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Predicted"
              stroke="#7c3aed"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="Observed"
              stroke="#2563eb"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
