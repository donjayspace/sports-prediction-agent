import { notFound } from "next/navigation";
import { getFixture, getPrediction, ApiError } from "@/lib/api-client";
import { PredictionCard } from "@/components/prediction-card";
import { ResearchPanel } from "@/components/research-panel";
import { ProbabilityChart } from "@/components/charts/probability-chart";

export const dynamic = "force-dynamic";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function MatchPage({ params }: Props): Promise<JSX.Element> {
  const { id } = await params;

  try {
    const [fixture, prediction] = await Promise.all([getFixture(id), getPrediction(id)]);

    const stat =
      prediction.statHome !== null &&
      prediction.statDraw !== null &&
      prediction.statAway !== null
        ? { home: prediction.statHome, draw: prediction.statDraw, away: prediction.statAway }
        : null;

    const llm =
      prediction.llmHome !== null &&
      prediction.llmDraw !== null &&
      prediction.llmAway !== null
        ? { home: prediction.llmHome, draw: prediction.llmDraw, away: prediction.llmAway }
        : null;

    const final = {
      home: prediction.finalHome,
      draw: prediction.finalDraw,
      away: prediction.finalAway,
    };

    return (
      <div className="space-y-6">
        <header>
          <h1 className="text-3xl font-bold">
            {fixture.homeTeam.name} vs {fixture.awayTeam.name}
          </h1>
          <p className="text-slate-400">
            {fixture.league} · {new Date(fixture.kickoffUtc).toLocaleString()}
          </p>
        </header>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <PredictionCard prediction={prediction} />
            <ProbabilityChart stat={stat} llm={llm} final={final} />
          </div>
          <ResearchPanel research={prediction.llmResearch} />
        </div>
      </div>
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }
}
