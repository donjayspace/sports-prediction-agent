import type { FastifyPluginAsync } from "fastify";
import { Sport } from "@prisma/client";
import { PerformanceService } from "../services/performance.service.js";

export const performanceRoutes: FastifyPluginAsync = async (app) => {
  const service = new PerformanceService(app);

  app.get("/performance/summary", async (req, reply) => {
    const { sport = "FOOTBALL", days = "30" } = req.query as {
      sport?: string;
      days?: string;
    };

    if (!Object.values(Sport).includes(sport as Sport)) {
      return reply.code(400).send({ error: "Invalid sport" });
    }

    const windowEnd = new Date();
    const windowStart = new Date(windowEnd.getTime() - Number.parseInt(days, 10) * 86_400_000);

    const summary = await service.evaluate(sport as Sport, windowStart, windowEnd);
    return reply.send(summary);
  });

  app.get("/performance/history", async (req, reply) => {
    const { sport } = req.query as { sport?: string };
    const evaluations = await app.prisma.evaluation.findMany({
      where: sport ? { sport: sport as Sport } : {},
      orderBy: { windowStart: "desc" },
      take: 90,
    });
    return reply.send(evaluations);
  });
};
