import type { PrismaClient } from "@prisma/client";

export class FixtureService {
  constructor(private readonly prisma: PrismaClient) {}

  list(input: { sport?: string; limit?: number }) {
    return this.prisma.event.findMany({
      where: input.sport ? { sport: input.sport } : undefined,
      orderBy: { startTime: "asc" },
      take: Math.min(Math.max(input.limit ?? 50, 1), 100)
    });
  }
}
