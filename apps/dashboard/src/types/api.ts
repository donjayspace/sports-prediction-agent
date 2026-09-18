export type Sport = "FOOTBALL" | "BASKETBALL" | "TENNIS" | "TABLE_TENNIS";
export type MatchStatus = "SCHEDULED" | "LIVE" | "COMPLETED" | "POSTPONED" | "CANCELLED";
export type Outcome = "HOME" | "DRAW" | "AWAY";

export interface Team {
  id: string;
  name: string;
  sport: Sport;
  country: string | null;
}

export interface PredictionSummary {
  finalHome: number;
  finalDraw: number;
  finalAway: number;
}

export interface Fixture {
  id: string;
  sport: Sport;
  league: string;
  status: MatchStatus;
  kickoffUtc: string;
  homeTeam: Team;
  awayTeam: Team;
  homeScore: number | null;
  awayScore: number | null;
  prediction: PredictionSummary | null;
}

export interface LlmResearch {
  injuries: string[];
  form_notes: string[];
  tactical_observations: string[];
  risk_factors: string[];
  raw_text: string | null;
}

export interface Prediction {
  id: string;
  fixtureId: string;
  statHome: number | null;
  statDraw: number | null;
  statAway: number | null;
  llmHome: number | null;
  llmDraw: number | null;
  llmAway: number | null;
  llmConfidence: number | null;
  llmProvider: string | null;
  llmResearch: LlmResearch | null;
  finalHome: number;
  finalDraw: number;
  finalAway: number;
  modelVersion: string;
  agentVersion: string;
  createdAt: string;
}

export interface PerformanceSummary {
  sport: Sport;
  nPredictions: number;
  brierScore: number;
  logLoss: number;
  accuracy: number;
  calibration: Array<{ bin: number; predicted: number; observed: number; count: number }>;
}
