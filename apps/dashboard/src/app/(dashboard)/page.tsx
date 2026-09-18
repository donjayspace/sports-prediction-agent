import Link from "next/link";
import { getUpcomingFixtures } from "@/lib/api-client";
import { LiveTicker } from "@/components/live-ticker";

export const dynamic = "force-dynamic";

export default async function OverviewPage(): Promise<JSX.Element> {
  const fixtures = await getUpcomingFixtures();
  const next = fixtures.slice(0, 8);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Overview</h1>
      <p className="text-slate-400">
        {fixtures.length} upcoming fixtures in the next 14 days.
      </p>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="rounded-lg border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
          <h2 className="mb-4 text-xl font-semibold">Next fixtures</h2>
          <ul className="divide-y divide-slate-800">
            {next.map((fx) => (
              <li key={fx.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium">
                    {fx.homeTeam.name} vs {fx.awayTeam.name}
                  </p>
                  <p className="text-sm text-slate-400">
                    {fx.league} · {new Date(fx.kickoffUtc).toLocaleString()}
                  </p>
                </div>
                <Link
                  href={`/match/${fx.id}`}
                  className="rounded bg-blue-600 px-3 py-1 text-sm hover:bg-blue-500"
                >
                  Analyze
                </Link>
              </li>
            ))}
          </ul>
        </section>

        <LiveTicker fixtures={fixtures} />
      </div>
    </div>
  );
}
