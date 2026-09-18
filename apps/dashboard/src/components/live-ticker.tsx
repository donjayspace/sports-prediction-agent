"use client";

import { useEffect, useState } from "react";
import type { Fixture } from "@/types/api";

interface LiveTickerProps {
  fixtures: Fixture[];
  intervalMs?: number;
}

export function LiveTicker({ fixtures, intervalMs = 30_000 }: LiveTickerProps): JSX.Element {
  const [now, setNow] = useState<number>(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  const upcoming = fixtures
    .map((f) => ({ fixture: f, ms: new Date(f.kickoffUtc).getTime() - now }))
    .filter((x) => x.ms > 0)
    .sort((a, b) => a.ms - b.ms)
    .slice(0, 5);

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">
        Kickoff countdown
      </h3>
      <ul className="space-y-2">
        {upcoming.map(({ fixture, ms }) => (
          <li key={fixture.id} className="flex items-center justify-between text-sm">
            <span className="text-slate-200">
              {fixture.homeTeam.name} vs {fixture.awayTeam.name}
            </span>
            <span className="font-mono text-blue-400">{formatDuration(ms)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatDuration(ms: number): string {
  const totalMinutes = Math.floor(ms / 60_000);
  const days = Math.floor(totalMinutes / (60 * 24));
  const hours = Math.floor((totalMinutes % (60 * 24)) / 60);
  const minutes = totalMinutes % 60;

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}
