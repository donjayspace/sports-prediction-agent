import type { FastifyInstance } from "fastify";
import { fixtureRoutes } from "./fixtures.js";
import { predictionRoutes } from "./predictions.js";
import { performanceRoutes } from "./performance.js";
import { agentRoutes } from "./agent.js";
import { healthRoutes } from "./health.js";

export async function registerRoutes(app: FastifyInstance) {
  await app.register(healthRoutes);
  await app.register(fixtureRoutes, { prefix: "/api/v1" });
  await app.register(predictionRoutes, { prefix: "/api/v1" });
  await app.register(performanceRoutes, { prefix: "/api/v1" });
  await app.register(agentRoutes, { prefix: "/api/v1" });
}
