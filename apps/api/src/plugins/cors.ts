import fp from "fastify-plugin";
import cors from "@fastify/cors";
import { env } from "../config/env.js";

export default fp(async (app) => {
  await app.register(cors, {
    origin: env.CORS_ORIGIN.split(",").map((value) => value.trim())
  });
});
