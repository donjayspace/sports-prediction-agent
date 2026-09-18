import type { FastifyInstance } from "fastify";

export async function predictionRoutes(app: FastifyInstance) {
  app.get("/predictions", async (request) => {
    const query = request.query as { eventId?: string; limit?: string };
    return app.predictionService.list({
      eventId: query.eventId,
      limit: query.limit ? Number(query.limit) : 50
    });
  });
}
