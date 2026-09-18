import type { FastifyPluginAsync } from "fastify";
import { AgentService } from "../services/agent.service.js";

export const agentRoutes: FastifyPluginAsync = async (app) => {
  const agent = new AgentService(app);

  app.post("/agent/analyze/:fixtureId", async (req, reply) => {
    const { fixtureId } = req.params as { fixtureId: string };

    try {
      const result = await agent.analyzeFixture(fixtureId);
      await agent.persistPrediction(fixtureId, result);
      return reply.code(201).send(result);
    } catch (err) {
      req.log.error({ err, fixtureId }, "Agent analysis failed");
      return reply.code(502).send({
        error: "Agent analysis failed",
        detail: err instanceof Error ? err.message : String(err),
      });
    }
  });
};
