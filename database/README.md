# Database

The API owns the Prisma schema in apps/api/prisma/schema.prisma.

Local setup: start PostgreSQL, set DATABASE_URL, generate Prisma Client, deploy migrations, then run the seed command.

Forecast records are point-in-time snapshots and retain model, feature, prompt, and data version metadata for reproducible evaluation.
