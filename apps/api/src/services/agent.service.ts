import { env } from "../config/env.js";

export class AgentService {
  async analyze(eventId: string) {
    const response = await fetch(`${env.AGENT_BASE_URL}/analyze/${encodeURIComponent(eventId)}`, {
      method: "POST",
      headers: { "content-type": "application/json" }
    });

    if (!response.ok) {
      throw new Error(`Agent request failed: ${response.status}`);
    }

    return response.json();
  }
}
