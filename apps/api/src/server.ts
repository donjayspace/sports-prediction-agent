import Fastify from "fastify";
import prisma from "./plugins/prisma.js";
import auth from "./plugins/auth.js";
import cors from "./plugins/cors.js";
import { env } from "./config/env.js";
import { registerRoutes } from "./routes/index.js";
import { FixtureService } from "./services/fixture.service.js";
import { PredictionService } from "./services/prediction.service.js";
import { PerformanceService } from "./services/performance.service.js";
import { AgentService } from "./services/agent.service.js";

declare module "fastify" {
  interface FastifyInstance {
    fixtureService: FixtureService;
    predictionService: PredictionService;
    performanceService: PerformanceService;
    agentService: AgentService;
  }
}

const app = Fastify({ logger: true });

await app.register(cors);
await app.register(auth);
await app.register(prisma);

app.decorate("fixtureService", new FixtureService(app.prisma));
app.decorate("predictionService", new PredictionService(app.prisma));
app.decorate("performanceService", new PerformanceService(app.prisma));
app.decorate("agentService", new AgentService());

await registerRoutes(app);

await app.listen({ host: env.HOST, port: env.PORT });
