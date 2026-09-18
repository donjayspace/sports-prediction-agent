import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";

const ProbabilitySchema = z.object({
  home: z.number().min(0).max(1),
  draw: z.number().min(0).max(1),
  away: z.number().min(0).max(1),
}).refine(
  (p) => Math.abs(p.home + p.draw + p.away - 1) < 1e-4,
  { message: "Probabilities must sum to 1" },
);

const AgentPayloadSchema = z.object({
  stat_probs: ProbabilitySchema,
  llm_probs: ProbabilitySchema,
  llm_confidence: z.number().min(0).max(1),
  llm_provider: z.string().min(1),
  llm_research: z.record(z.unknown()),
  final_probs: ProbabilitySchema,
  model_version: z.string().min(1),
  agent_version: z.string().min(1),
});

export const predictionRoutes: FastifyPluginAsync = async (app) => {
  app.get("/predictions/:fixtureId", async (req, reply) => {
    const { fixtureId } = req.params as { fixtureId: string };
    const prediction = await app.prisma.prediction.findUnique({
      where: { fixtureId },
      include: {
        fixture: { include: { homeTeam: true, awayTeam: true } },
      },
    });

    if (!prediction) return reply.code(404).send({ error: "Prediction not found" });
    return reply.send(prediction);
  });

  app.get("/predictions", async (req, reply) => {
    const { limit = "50" } = req.query as { limit?: string };
    const take = Math.min(Number.parseInt(limit, 10) || 50, 200);

    const predictions = await app.prisma.prediction.findMany({
      include: {
        fixture: {
          include: { homeTeam: true, awayTeam: true, result: true },
        },
      },
      orderBy: { createdAt: "desc" },
      take,
    });

    return reply.send(predictions);
  });

  app.post(
    "/internal/predictions/:fixtureId",
    { preHandler: [app.requireServiceToken] },
    async (req, reply) => {
      const { fixtureId } = req.params as { fixtureId: string };
      const parsed = AgentPayloadSchema.safeParse(req.body);
      if (!parsed.success) {
        return reply.code(400).send({ error: "Invalid payload", issues: parsed.error.issues });
      }

      const body = parsed.data;
      const data = {
        statHome: body.stat_probs.home,
        statDraw: body.stat_probs.draw,
        statAway: body.stat_probs.away,
        llmHome: body.llm_probs.home,
        llmDraw: body.llm_probs.draw,
        llmAway: body.llm_probs.away,
        llmConfidence: body.llm_confidence,
        llmProvider: body.llm_provider,
        llmResearch: body.llm_research,
        finalHome: body.final_probs.home,
        finalDraw: body.final_probs.draw,
        finalAway: body.final_probs.away,
        modelVersion: body.model_version,
        agentVersion: body.agent_version,
      };

      const prediction = await app.prisma.prediction.upsert({
        where: { fixtureId },
        create: { fixtureId, ...data },
        update: data,
      });

      return reply.code(201).send(prediction);
    },
  );
};
