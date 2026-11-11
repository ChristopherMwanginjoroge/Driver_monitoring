import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { LonLat, RouteCandidate } from "../types";

const NAIROBI_CENTER: LonLat = [36.8172, -1.2864];
const STYLE_URL = import.meta.env.VITE_MAP_STYLE_URL ?? "/style.json";

const ROUTE_COLORS = ["#38bdf8", "#a78bfa", "#f472b6", "#fbbf24"];

export interface TrafficMapProps {
  origin: LonLat | null;
  destination: LonLat | null;
  candidates: RouteCandidate[];
  selectedRank: number | null;
  onMapClick: (lonlat: LonLat) => void;
  accuracyMeters?: number | null;
}

export default function TrafficMap({
  origin,
  destination,
  candidates,
  selectedRank,
  onMapClick,
  accuracyMeters,
}: TrafficMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const originMarker = useRef<maplibregl.Marker | null>(null);
  const destMarker = useRef<maplibregl.Marker | null>(null);
  const clickHandlerRef = useRef(onMapClick);
  const [error, setError] = useState<string | null>(null);

  clickHandlerRef.current = onMapClick;

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    try {
      const map = new maplibregl.Map({
        container: containerRef.current,
        style: STYLE_URL,
        center: NAIROBI_CENTER,
        zoom: 11,
        attributionControl: { compact: true },
        failIfMajorPerformanceCaveat: false,
      });
      mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl(), "top-right");

    map.on("click", (e) => {
      clickHandlerRef.current([e.lngLat.lng, e.lngLat.lat]);
    });

    map.on("load", () => {
      map.addSource("routes", {
        type: "geojson",
        data: emptyFC(),
      });
      map.addLayer({
        id: "routes-casing",
        type: "line",
        source: "routes",
        paint: {
          "line-color": "#0f172a",
          "line-width": 8,
          "line-opacity": 0.5,
        },
      });
      map.addLayer({
        id: "routes-line",
        type: "line",
        source: "routes",
        paint: {
          "line-color": ["get", "color"],
          "line-width": [
            "case",
            ["==", ["get", "selected"], true],
            6,
            4,
          ],
          "line-opacity": [
            "case",
            ["==", ["get", "selected"], true],
            1.0,
            0.7,
          ],
        },
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to initialize map";
    setError(message);
    console.error("Map initialization error:", err);
  }
  }, [setError]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !origin) return;
    originMarker.current?.remove();
    originMarker.current = null;
    const el = document.createElement("div");
    el.style.width = "28px";
    el.style.height = "28px";
    el.style.borderRadius = "50%";
    el.style.backgroundColor = "#22c55e";
    el.style.border = "3px solid white";
    el.style.boxShadow = "0 0 0 6px rgba(34, 197, 94, 0.35)";
    el.className = "location-pin";
    originMarker.current = new maplibregl.Marker({ element: el })
      .setLngLat(origin)
      .setPopup(new maplibregl.Popup().setText("Your location"))
      .addTo(map);
    if (!destination) {
      map.flyTo({ center: origin, zoom: 14, duration: 1000 });
    }

    // Draw accuracy circle
    if (accuracyMeters && accuracyMeters > 0) {
      if (map.getSource("accuracy-circle")) {
        (map.getSource("accuracy-circle") as maplibregl.GeoJSONSource).setData({
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: origin,
          },
          properties: { buffer: accuracyMeters },
        });
      } else {
        map.addSource("accuracy-circle", {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: {
              type: "Point",
              coordinates: origin,
            },
            properties: { buffer: accuracyMeters },
          },
        });
        map.addLayer({
          id: "accuracy-circle-fill",
          type: "fill",
          source: "accuracy-circle",
          paint: {
            "fill-color": "#22c55e",
            "fill-opacity": 0.15,
          },
        });
        map.addLayer({
          id: "accuracy-circle-stroke",
          type: "line",
          source: "accuracy-circle",
          paint: {
            "line-color": "#22c55e",
            "line-width": 2,
            "line-opacity": 0.6,
          },
        });
        map.setPaintProperty(
          "accuracy-circle-fill",
          "fill-opacity",
          [
            "interpolate",
            ["linear"],
            ["zoom"],
            0,
            0.05,
            22,
            0.2,
          ],
        );
      }
    } else {
      if (map.getLayer("accuracy-circle-fill")) {
        map.removeLayer("accuracy-circle-fill");
      }
      if (map.getLayer("accuracy-circle-stroke")) {
        map.removeLayer("accuracy-circle-stroke");
      }
      if (map.getSource("accuracy-circle")) {
        map.removeSource("accuracy-circle");
      }
    }
  }, [origin, destination, accuracyMeters]);

  const styleEl = document.createElement("style");
  styleEl.textContent = `
    @keyframes pulse {
      0% { transform: scale(1); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.35); }
      70% { transform: scale(1.3); box-shadow: 0 0 0 14px rgba(34, 197, 94, 0); }
      100% { transform: scale(1); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.35); }
    }
  `;
  document.head.appendChild(styleEl);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    destMarker.current?.remove();
    destMarker.current = null;
    if (destination) {
      destMarker.current = new maplibregl.Marker({ color: "#ef4444" })
        .setLngLat(destination)
        .setPopup(new maplibregl.Popup().setText("Destination"))
        .addTo(map);
    }
  }, [destination]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const applyRoutes = () => {
      const source = map.getSource("routes") as maplibregl.GeoJSONSource | undefined;
      if (!source) return;
      source.setData(candidatesToFC(candidates, selectedRank));
      if (candidates.length > 0) {
        const bounds = new maplibregl.LngLatBounds();
        candidates.forEach((c) =>
          c.geometry.coordinates.forEach((p) => bounds.extend(p as [number, number])),
        );
        if (!bounds.isEmpty()) {
          map.fitBounds(bounds, { padding: 60, duration: 600, maxZoom: 15 });
        }
      }
    };
    if (map.isStyleLoaded()) applyRoutes();
    else map.once("load", applyRoutes);
  }, [candidates, selectedRank]);

  if (error) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-gray-700 font-semibold mb-2">Map unavailable</p>
          <p className="text-gray-500 text-sm max-w-xs">{error}</p>
        </div>
      </div>
    );
  }

  return <div ref={containerRef} className="absolute inset-0" />;
}

function emptyFC(): GeoJSON.FeatureCollection {
  return { type: "FeatureCollection", features: [] };
}

function candidatesToFC(
  candidates: RouteCandidate[],
  selectedRank: number | null,
): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: candidates.map((c) => ({
      type: "Feature",
      geometry: c.geometry,
      properties: {
        rank: c.rank,
        color: ROUTE_COLORS[c.rank % ROUTE_COLORS.length],
        selected: selectedRank === c.rank,
      },
    })),
  };
}
