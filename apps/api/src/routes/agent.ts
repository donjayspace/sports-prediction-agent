import type { FastifyInstance } from "fastify";

export async function agentRoutes(app: FastifyInstance) {
  app.post("/agent/analyze/:eventId", async (request) => {
    const params = request.params as { eventId: string };
    return app.agentService.analyze(params.eventId);
  });
}
