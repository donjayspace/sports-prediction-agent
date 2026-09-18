import fp from "fastify-plugin";
import fastifyJwt from "@fastify/jwt";
import { env } from "../config/env.js";

declare module "@fastify/jwt" {
  interface FastifyJWT {
    user: { sub: string; role: string };
  }
}

export default fp(async (app) => {
  await app.register(fastifyJwt, { secret: env.JWT_SECRET });
});
