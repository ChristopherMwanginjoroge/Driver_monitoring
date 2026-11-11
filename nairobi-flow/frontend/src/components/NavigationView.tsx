"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { LonLat, JourneyState } from "../types";
import {
  startJourney,
  submitJourneyLocation,
  pauseJourney,
  resumeJourney,
  completeJourney,
  rerouteJourney,
} from "../api/client";

const STYLE_URL = import.meta.env.VITE_MAP_STYLE_URL ?? "/style.json";

const ROUTE_COLOR = "#38bdf8";
const VEHICLE_COLOR = "#22c55e";

export interface NavigationViewProps {
  origin: LonLat;
  destination: LonLat;
  route: {
    geometry: { type: "LineString"; coordinates: [number, number][] };
    distance_m: number;
    duration_s: number;
  };
  onComplete: () => void;
}

export default function NavigationView({
  origin,
  destination,
  route,
  onComplete,
}: NavigationViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const vehicleMarkerRef = useRef<maplibregl.Marker | null>(null);
  const routeLayerRef = useRef<maplibregl.GeoJSONSource | null>(null);
  const watchIdRef = useRef<number | null>(null);
  const journeyIdRef = useRef<string | null>(null);
  const [journey, setJourney] = useState<JourneyState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [deviationWarning, setDeviationWarning] = useState(false);
  const [reroutePrompt, setReroutePrompt] = useState(false);

  const handleError = useCallback((msg: string) => {
    setError(msg);
    console.error(msg);
  }, []);

  // Update route line on map when the route geometry changes (reroute).
  useEffect(() => {
    const map = mapRef.current;
    const source = routeLayerRef.current;
    if (!map || !source) return;
    try {
      source.setData({
        type: "Feature",
        geometry: route.geometry,
        properties: {},
      });
    } catch {
      // ignore
    }
  }, [route.geometry]);

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    try {
      const map = new maplibregl.Map({
        container: containerRef.current,
        style: STYLE_URL,
        center: origin,
        zoom: 14,
        pitch: 45,
        bearing: 0,
        attributionControl: { compact: true },
        failIfMajorPerformanceCaveat: false,
      });
      mapRef.current = map;

      map.on("load", () => {
        map.addSource("nav-route", {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: route.geometry,
            properties: {},
          },
        });
        routeLayerRef.current = map.getSource(
          "nav-route"
        ) as maplibregl.GeoJSONSource;

        map.addLayer({
          id: "nav-route-casing",
          type: "line",
          source: "nav-route",
          paint: {
            "line-color": "#0f172a",
            "line-width": 10,
            "line-opacity": 0.4,
          },
        });
        map.addLayer({
          id: "nav-route-line",
          type: "line",
          source: "nav-route",
          paint: {
            "line-color": ROUTE_COLOR,
            "line-width": 6,
            "line-opacity": 0.9,
          },
        });

        const bounds = new maplibregl.LngLatBounds();
        route.geometry.coordinates.forEach((p) => bounds.extend(p));
        map.fitBounds(bounds, { padding: 80, duration: 800, maxZoom: 16 });

        new maplibregl.Marker({ color: "#22c55e" })
          .setLngLat(origin)
          .setPopup(new maplibregl.Popup().setText("Origin"))
          .addTo(map);

        new maplibregl.Marker({ color: "#ef4444" })
          .setLngLat(destination)
          .setPopup(new maplibregl.Popup().setText("Destination"))
          .addTo(map);

        const el = document.createElement("div");
        el.style.width = "24px";
        el.style.height = "24px";
        el.style.borderRadius = "50%";
        el.style.backgroundColor = VEHICLE_COLOR;
        el.style.border = "3px solid white";
        el.style.boxShadow = "0 2px 6px rgba(0,0,0,0.3)";
        el.style.transformOrigin = "center";
        vehicleMarkerRef.current = new maplibregl.Marker({
          element: el,
          rotation: 0,
        })
          .setLngLat(origin)
          .addTo(map);
      });
    } catch (err) {
      handleError(err instanceof Error ? err.message : "Map init failed");
    }

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
      if (journeyIdRef.current) {
        completeJourney(journeyIdRef.current).catch(() => {
          // ignore cleanup errors
        });
      }
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [containerRef.current, origin, destination, route.geometry, handleError]);

  // Start journey on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const started = await startJourney({
          origin,
          destination,
          route_geometry: route.geometry,
          route_distance_m: route.distance_m,
          route_duration_s: route.duration_s,
        });
        if (!cancelled) {
          setJourney(started);
          journeyIdRef.current = started.id;
          setIsNavigating(true);
        }
      } catch (e) {
        handleError(e instanceof Error ? e.message : "Failed to start journey");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [origin, destination, route, handleError]);

  // GPS watch + location submission
  useEffect(() => {
    if (!isNavigating || !journeyIdRef.current) return;

    if (!navigator.geolocation) {
      handleError("Geolocation not available");
      return;
    }

    const opts: PositionOptions = {
      enableHighAccuracy: true,
      maximumAge: 5000,
      timeout: 10000,
    };

    watchIdRef.current = navigator.geolocation.watchPosition(
      async (pos) => {
        const { longitude, latitude, speed, heading, accuracy } = pos.coords;
        const ll: LonLat = [longitude, latitude];

        const map = mapRef.current;
        const marker = vehicleMarkerRef.current;
        if (map && marker) {
          marker.setLngLat(ll);
          if (heading != null) {
            marker.setRotation(heading);
          }
          map.easeTo({
            center: ll,
            bearing: heading != null ? heading : 0,
            pitch: 45,
            duration: 1000,
          });
        }

        try {
          const updated: any = await submitJourneyLocation(
            journeyIdRef.current!,
            {
              longitude,
              latitude,
              speed_kmh: speed != null ? speed * 3.6 : undefined,
              heading_deg: heading != null ? heading : undefined,
              accuracy_m: accuracy != null ? accuracy : undefined,
              timestamp: new Date().toISOString(),
            }
          );
          setJourney(updated);

          // Deviation handling.
          const deviating = updated.deviating === true;
          const rerouted = updated.rerouted === true;
          setDeviationWarning(deviating && !rerouted);
          setReroutePrompt(deviating && !rerouted);
        } catch (e) {
          console.warn("Location submit failed:", e);
        }
      },
      (err) => {
        handleError(`GPS error: ${err.message}`);
      },
      opts,
    );

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
    };
  }, [isNavigating, journeyIdRef.current, handleError]);

  // Format helpers
  const fmtDuration = (s: number | null): string => {
    if (s == null) return "—";
    const m = Math.round(s / 60);
    if (m < 60) return `${m} min`;
    const h = Math.floor(m / 60);
    return `${h}h ${m - h * 60}m`;
  };

  const fmtDistance = (m: number | null): string => {
    if (m == null) return "—";
    if (m < 1000) return `${Math.round(m)} m`;
    return `${(m / 1000).toFixed(1)} km`;
  };

  const turnText = journey?.next_turn_instruction
    ? journey.next_turn_instruction
    : "Continue on route";

  if (error) {
    return (
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/90 text-rose-600 z-20 p-4 text-center">
        <h2 className="text-lg font-semibold mb-2">Navigation error</h2>
        <p className="text-sm mb-4">{error}</p>
        <button
          type="button"
          onClick={onComplete}
          className="rounded bg-sky-500 px-4 py-2 text-white font-medium hover:bg-sky-400"
        >
          Return to planning
        </button>
      </div>
    );
  }

  if (!journey) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-white/90 text-slate-600 z-20">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 rounded-full border-4 border-sky-200 border-t-sky-500 animate-spin" />
          <p className="text-sm">Starting navigation…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="absolute inset-0" />

      {/* Deviation warning banner */}
      {deviationWarning && !reroutePrompt && (
        <div className="absolute top-4 left-4 right-4 z-20">
          <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 font-bold mt-0.5">
                !
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-amber-800">
                  Off route
                </p>
                <p className="text-xs text-amber-700 mt-1">
                  You have left the planned route. Rerouting automatically…
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reroute prompt */}
      {reroutePrompt && (
        <div className="absolute top-4 left-4 right-4 z-20">
          <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 font-bold mt-0.5">
                !
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-amber-800">
                  Route recalculated
                </p>
                <p className="text-xs text-amber-700 mt-1">
                  New route follows current position to destination.
                </p>
              </div>
            </div>
            <div className="mt-3 flex justify-end">
              <button
                type="button"
                onClick={() => setReroutePrompt(false)}
                className="rounded bg-sky-500 px-4 py-2 text-sm text-white font-medium hover:bg-sky-400"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top navigation card */}
      <div className="absolute top-16 left-4 right-4 z-10">
        <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-slate-200 p-4">
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex-1">
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                Next turn
              </p>
              <p className="text-lg font-semibold text-slate-800">
                {turnText}
              </p>
              {journey.next_turn_distance_m != null && (
                <p className="text-sm text-slate-500">
                  in {fmtDistance(journey.next_turn_distance_m)}
                </p>
              )}
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                ETA
              </p>
              <p className="text-2xl font-bold text-sky-600">
                {fmtDuration(journey.eta_seconds)}
              </p>
            </div>
          </div>
          <div className="h-1 bg-slate-100 rounded-full overflow-hidden mt-3">
            <div
              className="h-full bg-sky-500 rounded-full transition-all duration-500"
              style={{
                width: journey.distance_remaining_m && route.distance_m
                  ? Math.max(
                      0,
                      Math.min(
                        100,
                        ((route.distance_m - journey.distance_remaining_m) /
                          route.distance_m) *
                          100,
                      ),
                    )
                  : 0,
              }}
            />
          </div>
          <p className="text-xs text-slate-400 mt-1 text-center">
            {fmtDistance(journey.distance_remaining_m)} remaining
          </p>
        </div>
      </div>

      {/* Bottom journey panel */}
      <div className="absolute bottom-4 left-4 right-4 z-10">
        <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                Journey status
              </p>
              <p className="text-sm font-semibold text-slate-800 capitalize">
                {journey.status}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() =>
                  journey.status === "active"
                    ? pauseJourney(journey.id).then(setJourney).catch(() => {})
                    : resumeJourney(journey.id).then(setJourney).catch(() => {})
                }
                className="rounded bg-slate-100 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-200 disabled:opacity-50"
              >
                {journey.status === "active" ? "Pause" : "Resume"}
              </button>
              <button
                type="button"
                onClick={() => rerouteJourney(journey.id).catch(() => {})}
                className="rounded bg-sky-50 px-3 py-1.5 text-sm text-sky-700 hover:bg-sky-100"
              >
                Reroute
              </button>
              <button
                type="button"
                onClick={() => {
                  completeJourney(journey.id).then(() => {
                    setIsNavigating(false);
                    onComplete();
                  }).catch(() => {});
                }}
                className="rounded bg-rose-50 px-3 py-1.5 text-sm text-rose-700 hover:bg-rose-100"
              >
                End Journey
              </button>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-slate-500 uppercase">Distance remaining</p>
              <p className="text-lg font-bold text-slate-800">
                {fmtDistance(journey.distance_remaining_m)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase">ETA</p>
              <p className="text-lg font-bold text-slate-800">
                {fmtDuration(journey.eta_seconds)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase">Status</p>
              <p className="text-lg font-bold text-slate-800 capitalize">
                {journey.status}
              </p>
            </div>
          </div>

          {journey.route_steps && journey.route_steps.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                Upcoming turns
              </p>
              <div className="space-y-1">
                                {journey.route_steps.slice(0, 3).map((step: any, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 px-3 py-1.5 rounded bg-slate-50 text-sm"
                  >
                    <span className="w-6 h-6 rounded-full bg-sky-100 flex items-center justify-center text-sky-700 text-xs font-bold">
                      {i + 1}
                    </span>
                    <span className="text-slate-700">{step.instruction}</span>
                    {step.distance_m != null && (
                      <span className="ml-auto text-xs text-slate-500">
                        {fmtDistance(step.distance_m)}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}