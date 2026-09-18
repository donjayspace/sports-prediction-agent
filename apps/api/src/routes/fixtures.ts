import type { FastifyInstance } from "fastify";

export async function fixtureRoutes(app: FastifyInstance) {
  app.get("/fixtures", async (request) => {
    const query = request.query as { sport?: string; limit?: string };
    return app.fixtureService.list({
      sport: query.sport,
      limit: query.limit ? Number(query.limit) : 50
    });
  });
}
