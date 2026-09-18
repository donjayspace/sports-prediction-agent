import Link from "next/link";
import { getPredictions } from "@/lib/api-client";

export const dynamic = "force-dynamic";

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export default async function PredictionsPage(): Promise<JSX.Element> {
  const predictions = await getPredictions(100);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Prediction history</h1>
      <div className="overflow-hidden rounded-lg border border-slate-800">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-left text-slate-400">
            <tr>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3">Fixture</th>
              <th className="px-4 py-3">Home</th>
              <th className="px-4 py-3">Draw</th>
              <th className="px-4 py-3">Away</th>
              <th className="px-4 py-3">Model</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {predictions.map((p) => (
              <tr key={p.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3">{new Date(p.createdAt).toLocaleString()}</td>
                <td className="px-4 py-3">
                  <Link href={`/match/${p.fixtureId}`} className="text-blue-400 hover:underline">
                    {p.fixtureId}
                  </Link>
                </td>
                <td className="px-4 py-3">{pct(p.finalHome)}</td>
                <td className="px-4 py-3">{pct(p.finalDraw)}</td>
                <td className="px-4 py-3">{pct(p.finalAway)}</td>
                <td className="px-4 py-3 text-xs text-slate-500">{p.modelVersion}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
