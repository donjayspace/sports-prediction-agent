import type { FastifyPluginAsync } from "fastify";
import { Sport, MatchStatus } from "@prisma/client";
import { z } from "zod";

const QuerySchema = z.object({
  sport: z.nativeEnum(Sport).optional(),
  status: z.nativeEnum(MatchStatus).optional(),
  from: z.coerce.date().optional(),
  to: z.coerce.date().optional(),
  limit: z.coerce.number().int().min(1).max(200).default(50),
});

export const fixtureRoutes: FastifyPluginAsync = async (app) => {
  app.get("/fixtures", async (req, reply) => {
    const parsed = QuerySchema.safeParse(req.query);
    if (!parsed.success) {
      return reply.code(400).send({ error: "Invalid query", issues: parsed.error.issues });
    }

    const { sport, status, from, to, limit } = parsed.data;

    const fixtures = await app.prisma.fixture.findMany({
      where: {
        ...(sport ? { sport } : {}),
        ...(status ? { status } : {}),
        ...(from || to
          ? {
              kickoffUtc: {
                ...(from ? { gte: from } : {}),
                ...(to ? { lte: to } : {}),
              },
            }
          : {}),
      },
      include: {
        homeTeam: true,
        awayTeam: true,
        prediction: { select: { finalHome: true, finalDraw: true, finalAway: true } },
      },
      orderBy: { kickoffUtc: "asc" },
      take: limit,
    });

    return reply.send(fixtures);
  });

  app.get("/fixtures/upcoming", async (_req, reply) => {
    const now = new Date();
    const horizon = new Date(now.getTime() + 1000 * 60 * 60 * 24 * 14);

    const fixtures = await app.prisma.fixture.findMany({
      where: {
        status: MatchStatus.SCHEDULED,
        kickoffUtc: { gte: now, lte: horizon },
      },
      include: { homeTeam: true, awayTeam: true },
      orderBy: { kickoffUtc: "asc" },
      take: 100,
    });

    return reply.send(fixtures);
  });

  app.get("/fixtures/:id", async (req, reply) => {
    const { id } = req.params as { id: string };
    const fixture = await app.prisma.fixture.findUnique({
      where: { id },
      include: {
        homeTeam: true,
        awayTeam: true,
        prediction: true,
        result: true,
        features: true,
      },
    });

    if (!fixture) return reply.code(404).send({ error: "Fixture not found" });
    return reply.send(fixture);
  });
};
