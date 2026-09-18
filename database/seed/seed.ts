import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.event.upsert({
    where: { id: "demo-football-001" },
    update: {},
    create: {
      id: "demo-football-001",
      sport: "football",
      competition: "Demo Research Competition",
      participants: ["Research Home", "Research Away"],
      homeName: "Research Home",
      awayName: "Research Away",
      startTime: new Date(Date.now() + 24 * 60 * 60 * 1000)
    }
  });
}

main().catch(console.error).finally(() => prisma.$disconnect());
