import type {
  JourneyLocationSubmit,
  JourneyStartRequest,
  JourneyState,
  LonLat,
  RouteRecommendation,
  Strategy,
} from "../types";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.error) detail = body.error;
      if (body?.detail) detail = `${detail}: ${body.detail}`;
    } catch {
      // response wasn't JSON
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<{ status: string }> {
  return jsonOrThrow(await fetch(`${BASE}/health/`));
}

export async function fetchNetworkGeoJSON(limit = 5000) {
  return jsonOrThrow<GeoJSON.FeatureCollection>(
    await fetch(`${BASE}/network/segments.geojson?limit=${limit}`),
  );
}

export async function recommendRoute(body: {
  origin: LonLat;
  destination: LonLat;
  departure_time: string;
  strategy: Strategy;
}): Promise<RouteRecommendation> {
  return jsonOrThrow<RouteRecommendation>(
    await fetch(`${BASE}/routes/recommend/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

export async function startJourney(body: JourneyStartRequest): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(
    await fetch(`${BASE}/journeys/start/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

export async function submitJourneyLocation(
  journeyId: string,
  body: JourneyLocationSubmit,
): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(
    await fetch(`${BASE}/journeys/${journeyId}/location/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

export async function getJourneyState(journeyId: string): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(await fetch(`${BASE}/journeys/${journeyId}/`));
}

export async function pauseJourney(journeyId: string): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(
    await fetch(`${BASE}/journeys/${journeyId}/pause/`, {
      method: "POST",
    }),
  );
}

export async function resumeJourney(journeyId: string): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(
    await fetch(`${BASE}/journeys/${journeyId}/resume/`, {
      method: "POST",
    }),
  );
}

export async function completeJourney(journeyId: string): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(
    await fetch(`${BASE}/journeys/${journeyId}/complete/`, {
      method: "POST",
    }),
  );
}

export async function rerouteJourney(journeyId: string): Promise<JourneyState> {
  return jsonOrThrow<JourneyState>(
    await fetch(`${BASE}/journeys/${journeyId}/reroute/`, {
      method: "POST",
    }),
  );
}
