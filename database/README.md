# Database

The Prisma schema is the single source of truth for the entire database.
It lives at `../apps/api/prisma/schema.prisma`.

## Why the schema lives with apps/api

Prisma generates a TypeScript client that is used exclusively by `apps/api`.
The Python agent never touches the database directly — it only calls
`apps/api` over HTTP. Keeping the schema co-located with the only writer
prevents drift and makes migrations atomic.

## Running migrations

```bash
pnpm db:generate     # regenerate Prisma client after schema changes
pnpm db:migrate      # create a new migration in development
pnpm db:deploy       # apply pending migrations in production
pnpm db:studio       # open Prisma Studio to inspect data
pnpm db:seed         # seed development fixtures
```
