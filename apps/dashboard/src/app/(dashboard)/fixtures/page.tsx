import Link from "next/link";
import { getFixtures } from "@/lib/api-client";

export const dynamic = "force-dynamic";

export default async function FixturesPage(): Promise<JSX.Element> {
  const fixtures = await getFixtures({ limit: 100 });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Fixtures</h1>
      <div className="overflow-hidden rounded-lg border border-slate-800">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-left text-slate-400">
            <tr>
              <th className="px-4 py-3">Kickoff</th>
              <th className="px-4 py-3">League</th>
              <th className="px-4 py-3">Match</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {fixtures.map((fx) => (
              <tr key={fx.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3">{new Date(fx.kickoffUtc).toLocaleString()}</td>
                <td className="px-4 py-3">{fx.league}</td>
                <td className="px-4 py-3">
                  {fx.homeTeam.name} vs {fx.awayTeam.name}
                </td>
                <td className="px-4 py-3">{fx.status}</td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/match/${fx.id}`}
                    className="rounded bg-blue-600 px-3 py-1 text-xs hover:bg-blue-500"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
