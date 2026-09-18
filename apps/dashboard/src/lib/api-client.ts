import type {
  Fixture,
  Prediction,
  PerformanceSummary,
  Sport,
} from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001";

class ApiError extends Error {
  public constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(`Request failed: ${res.status} ${body}`, res.status);
  }

  return (await res.json()) as T;
}

export async function getFixtures(params: { sport?: Sport; limit?: number } = {}): Promise<Fixture[]> {
  const search = new URLSearchParams();
  if (params.sport) search.set("sport", params.sport);
  if (params.limit) search.set("limit", String(params.limit));
  const qs = search.toString();

  return request<Fixture[]>(`/api/fixtures${qs ? `?${qs}` : ""}`, {
    next: { revalidate: 30 },
  } as RequestInit);
}

export async function getUpcomingFixtures(): Promise<Fixture[]> {
  return request<Fixture[]>("/api/fixtures/upcoming", {
    next: { revalidate: 60 },
  } as RequestInit);
}

export async function getFixture(id: string): Promise<Fixture> {
  return request<Fixture>(`/api/fixtures/${encodeURIComponent(id)}`, {
    next: { revalidate: 30 },
  } as RequestInit);
}

export async function getPrediction(fixtureId: string): Promise<Prediction> {
  return request<Prediction>(`/api/predictions/${encodeURIComponent(fixtureId)}`, {
    next: { revalidate: 30 },
  } as RequestInit);
}

export async function getPredictions(limit = 50): Promise<Prediction[]> {
  return request<Prediction[]>(`/api/predictions?limit=${limit}`, {
    next: { revalidate: 30 },
  } as RequestInit);
}

export async function getPerformance(sport: Sport, days = 30): Promise<PerformanceSummary> {
  return request<PerformanceSummary>(
    `/api/performance/summary?sport=${sport}&days=${days}`,
    { next: { revalidate: 120 } } as RequestInit,
  );
}
