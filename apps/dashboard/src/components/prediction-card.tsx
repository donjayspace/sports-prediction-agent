import type { Prediction } from "@/types/api";

interface Props {
  prediction: Prediction;
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function PredictionCard({ prediction }: Props): JSX.Element {
  const rows: Array<{ label: string; stat: number | null; llm: number | null; final: number }> = [
    { label: "Home", stat: prediction.statHome, llm: prediction.llmHome, final: prediction.finalHome },
    { label: "Draw", stat: prediction.statDraw, llm: prediction.llmDraw, final: prediction.finalDraw },
    { label: "Away", stat: prediction.statAway, llm: prediction.llmAway, final: prediction.finalAway },
  ];

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-4 text-xl font-semibold">Prediction</h2>
      <table className="w-full text-sm">
        <thead className="text-left text-slate-400">
          <tr>
            <th className="py-2">Outcome</th>
            <th className="py-2">Statistical</th>
            <th className="py-2">LLM</th>
            <th className="py-2">Final</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-t border-slate-800">
              <td className="py-2 font-medium">{row.label}</td>
              <td className="py-2">{row.stat !== null ? pct(row.stat) : "—"}</td>
              <td className="py-2">{row.llm !== null ? pct(row.llm) : "—"}</td>
              <td className="py-2 font-semibold text-blue-400">{pct(row.final)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-4 text-xs text-slate-500">
        Model: {prediction.modelVersion} · Agent: {prediction.agentVersion}
        {prediction.llmConfidence !== null && ` · LLM confidence: ${pct(prediction.llmConfidence)}`}
      </p>
    </div>
  );
}
