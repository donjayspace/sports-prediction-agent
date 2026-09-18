import type { FastifyInstance } from "fastify";
import { AgentRunKind, AgentRunStatus, Prisma } from "@prisma/client";
import { env } from "../config/env.js";

export interface AgentAnalyzePayload {
  fixture_id: string;
  sport: string;
  home_team: string;
  away_team: string;
  kickoff_utc: string;
  league: string;
}

export interface AgentAnalyzeResult {
  stat_probs: { home: number; draw: number; away: number };
  llm_probs: { home: number; draw: number; away: number };
  llm_confidence: number;
  llm_provider: string;
  llm_research: Record<string, unknown>;
  final_probs: { home: number; draw: number; away: number };
  model_version: string;
  agent_version: string;
}

const AGENT_TIMEOUT_MS = 90_000;

export class AgentService {
  public constructor(private readonly app: FastifyInstance) {}

  public async analyzeFixture(fixtureId: string): Promise<AgentAnalyzeResult> {
    const fixture = await this.app.prisma.fixture.findUniqueOrThrow({
      where: { id: fixtureId },
      include: { homeTeam: true, awayTeam: true },
    });

    const run = await this.app.prisma.agentRun.create({
      data: {
        fixtureId,
        kind: AgentRunKind.ANALYZE,
        status: AgentRunStatus.RUNNING,
      },
    });

    const payload: AgentAnalyzePayload = {
      fixture_id: fixture.id,
      sport: fixture.sport.toLowerCase(),
      home_team: fixture.homeTeam.name,
      away_team: fixture.awayTeam.name,
      kickoff_utc: fixture.kickoffUtc.toISOString(),
      league: fixture.league,
    };

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), AGENT_TIMEOUT_MS);

    try {
      const res = await fetch(`${env.AGENT_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Service-Token": env.AGENT_SERVICE_TOKEN,
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Agent responded ${res.status}: ${body}`);
      }

      const result = (await res.json()) as AgentAnalyzeResult;

      await this.app.prisma.agentRun.update({
        where: { id: run.id },
        data: {
          status: AgentRunStatus.SUCCESS,
          finishedAt: new Date(),
          metadata: { model_version: result.model_version } as Prisma.InputJsonValue,
        },
      });

      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      await this.app.prisma.agentRun.update({
        where: { id: run.id },
        data: {
          status: AgentRunStatus.FAILED,
          finishedAt: new Date(),
          error: message,
        },
      });
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }

  public async persistPrediction(
    fixtureId: string,
    result: AgentAnalyzeResult,
  ): Promise<void> {
    const data = {
      statHome: result.stat_probs.home,
      statDraw: result.stat_probs.draw,
      statAway: result.stat_probs.away,
      llmHome: result.llm_probs.home,
      llmDraw: result.llm_probs.draw,
      llmAway: result.llm_probs.away,
      llmConfidence: result.llm_confidence,
      llmProvider: result.llm_provider,
      llmResearch: result.llm_research as Prisma.InputJsonValue,
      finalHome: result.final_probs.home,
      finalDraw: result.final_probs.draw,
      finalAway: result.final_probs.away,
      modelVersion: result.model_version,
      agentVersion: result.agent_version,
    };

    await this.app.prisma.prediction.upsert({
      where: { fixtureId },
      create: { fixtureId, ...data },
      update: data,
    });
  }
}
