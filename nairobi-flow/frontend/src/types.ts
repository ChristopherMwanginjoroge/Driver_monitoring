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

export type JourneyStatus = "active" | "paused" | "completed" | "cancelled";

export interface JourneyState {
  id: string;
  origin_lon: number | null;
  origin_lat: number | null;
  destination_lon: number | null;
  destination_lat: number | null;
  status: JourneyStatus;
  current_lon: number | null;
  current_lat: number | null;
  distance_remaining_m: number | null;
  eta_seconds: number | null;
  next_turn_instruction: string;
  next_turn_distance_m: number | null;
  route_steps: Array<{
    instruction: string;
    distance_m: number | null;
    duration_s: number | null;
    type: string;
    modifier: string | null;
    location: [number, number] | null;
  }>;
  started_at: string;
  updated_at: string;
  ended_at: string | null;
  client_id: string;
}

export interface JourneyStartRequest {
  origin: LonLat;
  destination: LonLat;
  route_geometry?: { type: "LineString"; coordinates: [number, number][] };
  route_distance_m?: number;
  route_duration_s?: number;
  client_id?: string;
}

export interface JourneyLocationSubmit {
  longitude: number;
  latitude: number;
  speed_kmh?: number;
  heading_deg?: number;
  accuracy_m?: number;
  timestamp?: string;
}
