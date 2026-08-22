export type Strategy = "conventional" | "predictive" | "network_aware";

export type LonLat = [number, number];

export interface RouteCandidate {
  rank: number;
  geometry: { type: "LineString"; coordinates: [number, number][] };
  current_travel_time_s: number;
  predicted_travel_time_s: number;
  risk_level: string;
  strategy: Strategy;
  distance_m: number;
}

export interface RouteRecommendation {
  request_id: number;
  strategy: Strategy;
  candidates: RouteCandidate[];
}
