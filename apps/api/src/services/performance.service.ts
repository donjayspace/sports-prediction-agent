import type { PrismaClient } from "@prisma/client";

export class PerformanceService {
  constructor(private readonly prisma: PrismaClient) {}

  async summary() {
    const evaluations = await this.prisma.forecastEvaluation.findMany();
    if (!evaluations.length) return { samples: 0, accuracy: null, brierScore: null, logLoss: null };

    const accuracy = evaluations.filter((item) => item.correct).length / evaluations.length;
    const brierScore = evaluations.reduce((sum, item) => sum + item.brierScore, 0) / evaluations.length;
    const logLoss = evaluations.reduce((sum, item) => sum + item.logLoss, 0) / evaluations.length;

    return { samples: evaluations.length, accuracy, brierScore, logLoss };
  }
}
