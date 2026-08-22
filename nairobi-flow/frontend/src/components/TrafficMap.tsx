import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { LonLat, RouteCandidate } from "../types";

const NAIROBI_CENTER: LonLat = [36.8172, -1.2864];
const STYLE_URL =
  import.meta.env.VITE_MAP_STYLE_URL ??
  "https://demotiles.maplibre.org/style.json";

const ROUTE_COLORS = ["#38bdf8", "#a78bfa", "#f472b6", "#fbbf24"];

export interface TrafficMapProps {
  origin: LonLat | null;
  destination: LonLat | null;
  candidates: RouteCandidate[];
  selectedRank: number | null;
  onMapClick: (lonlat: LonLat) => void;
}

export default function TrafficMap({
  origin,
  destination,
  candidates,
  selectedRank,
  onMapClick,
}: TrafficMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const originMarker = useRef<maplibregl.Marker | null>(null);
  const destMarker = useRef<maplibregl.Marker | null>(null);
  const clickHandlerRef = useRef(onMapClick);

  clickHandlerRef.current = onMapClick;

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: STYLE_URL,
      center: NAIROBI_CENTER,
      zoom: 11,
      attributionControl: { compact: true },
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
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    originMarker.current?.remove();
    originMarker.current = null;
    if (origin) {
      originMarker.current = new maplibregl.Marker({ color: "#22c55e" })
        .setLngLat(origin)
        .setPopup(new maplibregl.Popup().setText("Origin"))
        .addTo(map);
    }
  }, [origin]);

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
