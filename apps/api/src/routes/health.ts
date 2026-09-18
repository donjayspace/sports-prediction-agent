import type { FastifyPluginAsync } from "fastify";

export const healthRoutes: FastifyPluginAsync = async (app) => {
  app.get("/health", async () => ({
    status: "ok",
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  }));

  app.get("/health/deep", async (_req, reply) => {
    const checks: Record<string, "ok" | "fail"> = {};

    try {
      await app.prisma.$queryRaw`SELECT 1`;
      checks.database = "ok";
    } catch {
      checks.database = "fail";
    }

    try {
      await app.redis.ping();
      checks.redis = "ok";
    } catch {
      checks.redis = "fail";
    }

    const healthy = Object.values(checks).every((v) => v === "ok");
    return reply.code(healthy ? 200 : 503).send({ status: healthy ? "ok" : "degraded", checks });
  });
};
