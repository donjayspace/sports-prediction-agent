import type { FastifyPluginAsync } from "fastify";
import { Sport, MatchStatus, Prisma } from "@prisma/client";
import { z } from "zod";

const QuerySchema = z.object({
  sport: z.nativeEnum(Sport).optional(),
  status: z.nativeEnum(MatchStatus).optional(),
  from: z.coerce.date().optional(),
  to: z.coerce.date().optional(),
  limit: z.coerce.number().int().min(1).max(200).default(50),
});

const IngestSchema = z.object({
  externalId: z.string().min(1),
  sport: z.nativeEnum(Sport),
  league: z.string().min(1),
  homeTeamName: z.string().min(1),
  awayTeamName: z.string().min(1),
  kickoffUtc: z.coerce.date(),
});

async function ensureTeam(
  app: Parameters<FastifyPluginAsync>[0],
  name: string,
  sport: Sport,
): Promise<{ id: string }> {
  return app.prisma.team.upsert({
    where: { sport_name: { sport, name } },
    update: {},
    create: { name, sport },
    select: { id: true },
  });
}

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

  app.post(
    "/fixtures/ingest",
    { preHandler: [app.requireServiceToken] },
    async (req, reply) => {
      const parsed = IngestSchema.safeParse(req.body);
      if (!parsed.success) {
        return reply.code(400).send({ error: "Invalid payload", issues: parsed.error.issues });
      }

      const body = parsed.data;
      const [homeTeam, awayTeam] = await Promise.all([
        ensureTeam(app, body.homeTeamName, body.sport),
        ensureTeam(app, body.awayTeamName, body.sport),
      ]);

      const existing = await app.prisma.fixture.findUnique({
        where: { externalId: body.externalId },
        include: { homeTeam: true, awayTeam: true },
      });

      if (existing) {
        const updated = await app.prisma.fixture.update({
          where: { id: existing.id },
          data: {
            kickoffUtc: body.kickoffUtc,
            league: body.league,
            homeTeamId: homeTeam.id,
            awayTeamId: awayTeam.id,
          },
          include: { homeTeam: true, awayTeam: true },
        });
        return reply.send(updated);
      }

      const created = await app.prisma.fixture.create({
        data: {
          externalId: body.externalId,
          sport: body.sport,
          league: body.league,
          status: MatchStatus.SCHEDULED,
          kickoffUtc: body.kickoffUtc,
          homeTeamId: homeTeam.id,
          awayTeamId: awayTeam.id,
        },
        include: { homeTeam: true, awayTeam: true },
      });

      return reply.code(201).send(created);
    },
  );

  app.post(
    "/fixtures/refresh",
    { preHandler: [app.requireServiceToken] },
    async (req, reply) => {
      const now = new Date();
      const stale = await app.prisma.fixture.findMany({
        where: {
          status: MatchStatus.SCHEDULED,
          kickoffUtc: { lt: now },
        },
        select: { id: true },
      });

      if (stale.length === 0) return reply.send({ updated: 0 });

      const result = await app.prisma.fixture.updateMany({
        where: { id: { in: stale.map((f) => f.id) } },
        data: { status: MatchStatus.LIVE },
      });

      req.log.info({ updated: result.count }, "Marked stale fixtures as LIVE");
      return reply.send({ updated: result.count });
    },
  );

  app.post(
    "/fixtures/:id/result",
    { preHandler: [app.requireServiceToken] },
    async (req, reply) => {
      const { id } = req.params as { id: string };
      const ResultSchema = z.object({
        homeScore: z.number().int().min(0),
        awayScore: z.number().int().min(0),
      });

      const parsed = ResultSchema.safeParse(req.body);
      if (!parsed.success) {
        return reply.code(400).send({ error: "Invalid payload", issues: parsed.error.issues });
      }

      const { homeScore, awayScore } = parsed.data;
      const outcome = homeScore > awayScore ? "HOME" : homeScore < awayScore ? "AWAY" : "DRAW";

      const fixture = await app.prisma.fixture.findUnique({ where: { id } });
      if (!fixture) return reply.code(404).send({ error: "Fixture not found" });

      const [updatedFixture, result] = await app.prisma.$transaction([
        app.prisma.fixture.update({
          where: { id },
          data: {
            homeScore,
            awayScore,
            status: MatchStatus.COMPLETED,
          },
        }),
        app.prisma.result.upsert({
          where: { fixtureId: id },
          create: { fixtureId: id, homeScore, awayScore, outcome },
          update: { homeScore, awayScore, outcome },
        }),
      ]);

      req.log.info({ fixtureId: id, outcome }, "Fixture result recorded");
      return reply.send({ fixture: updatedFixture, result });
    },
  );

  app.get("/fixtures/stats/leagues", async (_req, reply) => {
    const rows = await app.prisma.$queryRaw<Array<{ league: string; count: bigint }>>(
      Prisma.sql`
        SELECT league, COUNT(*)::bigint AS count
        FROM "Fixture"
        WHERE "kickoffUtc" >= NOW()
        GROUP BY league
        ORDER BY count DESC
        LIMIT 20
      `,
    );

    return reply.send(rows.map((r) => ({ league: r.league, count: Number(r.count) })));
  });
};
