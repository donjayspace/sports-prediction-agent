import Fastify from "fastify";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";
import { env } from "./config/env.js";
import prismaPlugin from "./plugins/prisma.js";
import redisPlugin from "./plugins/redis.js";
import authPlugin from "./plugins/auth.js";
import { healthRoutes } from "./routes/health.js";
import { fixtureRoutes } from "./routes/fixtures.js";
import { predictionRoutes } from "./routes/predictions.js";
import { performanceRoutes } from "./routes/performance.js";
import { agentRoutes } from "./routes/agent.js";

const app = Fastify({
  logger: {
    level: env.LOG_LEVEL,
    ...(env.NODE_ENV === "development"
      ? { transport: { target: "pino-pretty", options: { colorize: true } } }
      : {}),
  },
  trustProxy: true,
  bodyLimit: 1_048_576,
});

async function bootstrap(): Promise<void> {
  await app.register(cors, {
    origin: env.NODE_ENV === "production" ? [env.API_PUBLIC_URL] : true,
    credentials: true,
  });

  await app.register(rateLimit, { max: 300, timeWindow: "1 minute" });

  await app.register(prismaPlugin);
  await app.register(redisPlugin);
  await app.register(authPlugin);

  await app.register(healthRoutes);
  await app.register(fixtureRoutes, { prefix: "/api" });
  await app.register(predictionRoutes, { prefix: "/api" });
  await app.register(performanceRoutes, { prefix: "/api" });
  await app.register(agentRoutes, { prefix: "/api/internal" });

  const shutdown = async (signal: string): Promise<void> => {
    app.log.info({ signal }, "Shutting down");
    await app.close();
    process.exit(0);
  };

  process.on("SIGINT", () => void shutdown("SIGINT"));
  process.on("SIGTERM", () => void shutdown("SIGTERM"));

  await app.listen({ port: env.API_PORT, host: "0.0.0.0" });
}

bootstrap().catch((err: unknown) => {
  app.log.fatal({ err }, "Fatal startup error");
  process.exit(1);
});
