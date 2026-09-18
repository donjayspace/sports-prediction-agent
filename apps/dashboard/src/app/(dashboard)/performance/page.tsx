import { getPerformance } from "@/lib/api-client";
import { CalibrationChart } from "@/components/calibration-chart";

export const dynamic = "force-dynamic";

export default async function PerformancePage(): Promise<JSX.Element> {
  const summary = await getPerformance("FOOTBALL", 30);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Performance (last 30 days)</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Predictions" value={String(summary.nPredictions)} />
        <Stat label="Accuracy" value={`${(summary.accuracy * 100).toFixed(1)}%`} />
        <Stat label="Brier score" value={summary.brierScore.toFixed(4)} />
        <Stat label="Log loss" value={summary.logLoss.toFixed(4)} />
      </div>

      {summary.calibration.length > 0 ? (
        <CalibrationChart points={summary.calibration} />
      ) : (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
          No resolved predictions in the selected window yet.
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }): JSX.Element {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}
