import type { FastifyInstance } from "fastify";

export async function performanceRoutes(app: FastifyInstance) {
  app.get("/performance", async () => app.performanceService.summary());
}
