export interface AgentAnalyzeRequest {
  fixture_id: string;
  sport: string;
  home_team: string;
  away_team: string;
  kickoff_utc: string;
  league: string;
}

export interface ProbabilityTriple {
  home: number;
  draw: number;
  away: number;
}

export interface LlmResearchPayload {
  injuries: string[];
  form_notes: string[];
  tactical_observations: string[];
  risk_factors: string[];
  raw_text: string | null;
}

export interface AgentAnalyzeResponse {
  stat_probs: ProbabilityTriple;
  llm_probs: ProbabilityTriple;
  llm_confidence: number;
  llm_provider: string;
  llm_research: LlmResearchPayload;
  final_probs: ProbabilityTriple;
  model_version: string;
  agent_version: string;
}
