import type { FastifyInstance } from "fastify";
import { Outcome, Sport } from "@prisma/client";

export interface EvaluationSummary {
  sport: Sport;
  nPredictions: number;
  brierScore: number;
  logLoss: number;
  accuracy: number;
  calibration: Array<{ bin: number; predicted: number; observed: number; count: number }>;
}

const OUTCOMES: readonly Outcome[] = [Outcome.HOME, Outcome.DRAW, Outcome.AWAY] as const;

function outcomeFromScores(home: number, away: number): Outcome {
  if (home > away) return Outcome.HOME;
  if (home < away) return Outcome.AWAY;
  return Outcome.DRAW;
}

function logSafe(value: number): number {
  return Math.log(Math.max(Math.min(value, 1 - 1e-12), 1e-12));
}

export class PerformanceService {
  public constructor(private readonly app: FastifyInstance) {}

  public async evaluate(
    sport: Sport,
    windowStart: Date,
    windowEnd: Date,
  ): Promise<EvaluationSummary> {
    const fixtures = await this.app.prisma.fixture.findMany({
      where: {
        sport,
        status: "COMPLETED",
        kickoffUtc: { gte: windowStart, lte: windowEnd },
        prediction: { isNot: null },
        result: { isNot: null },
      },
      include: { prediction: true, result: true },
    });

    let brierSum = 0;
    let logLossSum = 0;
    let correct = 0;
    let n = 0;

    const bins: Array<{ pSum: number; ySum: number; count: number }> = Array.from(
      { length: 10 },
      () => ({ pSum: 0, ySum: 0, count: 0 }),
    );

    for (const fixture of fixtures) {
      const prediction = fixture.prediction;
      const result = fixture.result;
      if (!prediction || !result) continue;

      const truth = result.outcome;
      const probs: Record<Outcome, number> = {
        [Outcome.HOME]: prediction.finalHome,
        [Outcome.DRAW]: prediction.finalDraw,
        [Outcome.AWAY]: prediction.finalAway,
      };

      const expectedOutcome = outcomeFromScores(result.homeScore, result.awayScore);
      if (expectedOutcome !== truth) continue;

      let brier = 0;
      for (const o of OUTCOMES) {
        const y = o === truth ? 1 : 0;
        const p = probs[o];
        brier += (p - y) ** 2;

        const binIdx = Math.min(9, Math.floor(p * 10));
        const bin = bins[binIdx];
        if (bin) {
          bin.pSum += p;
          bin.ySum += y;
          bin.count += 1;
        }
      }
      brierSum += brier;

      logLossSum += logSafe(probs[truth]);

      const argmax = OUTCOMES.reduce((best, o) => (probs[o] > probs[best] ? o : best), OUTCOMES[0]!);
      if (argmax === truth) correct += 1;

      n += 1;
    }

    if (n === 0) {
      return {
        sport,
        nPredictions: 0,
        brierScore: 0,
        logLoss: 0,
        accuracy: 0,
        calibration: [],
      };
    }

    const calibration = bins
      .map((bin, i) => ({
        bin: i,
        predicted: bin.count > 0 ? bin.pSum / bin.count : 0,
        observed: bin.count > 0 ? bin.ySum / bin.count : 0,
        count: bin.count,
      }))
      .filter((b) => b.count > 0);

    const summary: EvaluationSummary = {
      sport,
      nPredictions: n,
      brierScore: brierSum / n,
      logLoss: logLossSum / n,
      accuracy: correct / n,
      calibration,
    };

    await this.app.prisma.evaluation.create({
      data: {
        sport,
        windowStart,
        windowEnd,
        nPredictions: n,
        brierScore: summary.brierScore,
        logLoss: summary.logLoss,
        accuracy: summary.accuracy,
        calibrationJson: calibration,
        modelVersion: fixtures[0]?.prediction?.modelVersion ?? "unknown",
      },
    });

    return summary;
  }
        }
