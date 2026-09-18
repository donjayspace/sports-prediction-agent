import type { PrismaClient } from "@prisma/client";

export class PredictionService {
  constructor(private readonly prisma: PrismaClient) {}

  list(input: { eventId?: string; limit?: number }) {
    return this.prisma.forecast.findMany({
      where: input.eventId ? { eventId: input.eventId } : undefined,
      orderBy: { createdAt: "desc" },
      take: Math.min(Math.max(input.limit ?? 50, 1), 100)
    });
  }
}
