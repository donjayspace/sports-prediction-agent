import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  LOG_LEVEL: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
  API_PORT: z.coerce.number().int().positive().default(3001),
  API_PUBLIC_URL: z.string().url().default("http://localhost:3001"),
  DATABASE_URL: z.string().min(1, "DATABASE_URL is required"),
  REDIS_URL: z.string().min(1, "REDIS_URL is required"),
  AGENT_URL: z.string().url().default("http://localhost:8000"),
  AGENT_SERVICE_TOKEN: z.string().min(16, "AGENT_SERVICE_TOKEN must be at least 16 chars"),
  JWT_SECRET: z.string().min(16, "JWT_SECRET must be at least 16 chars"),
});

export type Env = z.infer<typeof EnvSchema>;

function loadEnv(): Env {
  const parsed = EnvSchema.safeParse(process.env);
  if (!parsed.success) {
    const issues = parsed.error.issues
      .map((i) => `  - ${i.path.join(".")}: ${i.message}`)
      .join("\n");
    throw new Error(`Invalid environment variables:\n${issues}`);
  }
  return parsed.data;
}

export const env: Env = loadEnv();
