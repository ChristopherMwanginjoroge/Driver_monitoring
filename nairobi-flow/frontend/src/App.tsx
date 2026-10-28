import { useCallback, useEffect, useMemo, useState } from "react";
import TrafficMap from "./components/TrafficMap";
import TopBar from "./components/TopBar";
import BottomSheet, { type BottomSheetTab } from "./components/BottomSheet";
import MapControls from "./components/MapControls";
import { fetchHealth, recommendRoute } from "./api/client";
import type { LonLat, RouteCandidate, RouteRecommendation, Strategy } from "./types";

function defaultDepartureLocal(): string {
  const now = new Date();
  now.setSeconds(0, 0);
  const tzOffsetMs = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - tzOffsetMs).toISOString().slice(0, 16);
}

function localToIso(local: string): string {
  return new Date(local).toISOString();
}

function parseLonLat(s: string): LonLat | null {
  const parts = s.split(",").map((p) => parseFloat(p.trim()));
  if (parts.length === 2 && parts.every((n) => !isNaN(n))) {
    return [parts[0], parts[1]];
  }
  return null;
}

export default function App() {
  const [health, setHealth] = useState<string>("checking…");
  const [origin, setOrigin] = useState<LonLat | null>(null);
  const [destination, setDestination] = useState<LonLat | null>(null);
  const [strategy, setStrategy] = useState<Strategy>("conventional");
  const [departureTime, setDepartureTime] = useState<string>(
    () => defaultDepartureLocal(),
  );
  const [candidates, setCandidates] = useState<RouteCandidate[]>([]);
  const [selectedRank, setSelectedRank] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<BottomSheetTab>("input");

  const locateMe = useCallback(() => {
    if (!navigator.geolocation) {
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const ll: LonLat = [pos.coords.longitude, pos.coords.latitude];
        setOrigin(ll);
      },
      (err) => {
        console.warn("Geolocation error:", err);
      },
      { enableHighAccuracy: true, maximumAge: 30000, timeout: 5000 },
    );
  }, []);

  useEffect(() => {
    fetchHealth()
      .then((h) => setHealth(h.status))
      .catch(() => setHealth("unreachable"));
  }, []);

  useEffect(() => {
    locateMe();
  }, [locateMe]);

  const originInput = useMemo(
    () => (origin ? `${origin[0].toFixed(4)}, ${origin[1].toFixed(4)}` : ""),
    [origin],
  );

  const destinationInput = useMemo(
    () => (destination ? `${destination[0].toFixed(4)}, ${destination[1].toFixed(4)}` : ""),
    [destination],
  );

  const handleMapClick = useCallback(
    (p: LonLat) => {
      if (!origin) setOrigin(p);
      else setDestination(p);
    },
    [origin],
  );

  const onOriginChange = useCallback(
    (v: string) => {
      const parsed = parseLonLat(v);
      if (parsed) setOrigin(parsed);
    },
    [],
  );

  const onDestinationChange = useCallback(
    (v: string) => {
      const parsed = parseLonLat(v);
      if (parsed) setDestination(parsed);
    },
    [],
  );

  const onOriginBlur = useCallback(() => {
    const parsed = parseLonLat(originInput);
    if (parsed) setOrigin(parsed);
  }, [originInput]);

  const onDestinationBlur = useCallback(() => {
    const parsed = parseLonLat(destinationInput);
    if (parsed) setDestination(parsed);
  }, [destinationInput]);

  const handleOriginKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        e.preventDefault();
        onOriginBlur();
      }
    },
    [onOriginBlur],
  );

  const handleDestinationKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        e.preventDefault();
        onDestinationBlur();
      }
    },
    [onDestinationBlur],
  );

  const swap = useCallback(() => {
    setOrigin(destination);
    setDestination(origin);
  }, [origin, destination]);

  const submit = useCallback(async () => {
    if (!origin || !destination) return;
    setLoading(true);
    setError(null);
    try {
      const iso = localToIso(departureTime);
      const res: RouteRecommendation = await recommendRoute({
        origin,
        destination,
        departure_time: iso,
        strategy,
      });
      setCandidates(res.candidates);
      setSelectedRank(res.candidates[0]?.rank ?? null);
      setTab("routes");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setCandidates([]);
      setSelectedRank(null);
    } finally {
      setLoading(false);
    }
  }, [origin, destination, departureTime, strategy]);

  const healthClass = useMemo(
    () =>
      health === "ok"
        ? "text-emerald-400"
        : health === "checking…"
          ? "text-slate-400"
          : "text-rose-400",
    [health],
  );

  const startDrive = useCallback(() => {
    alert("Starting navigation in Nairobi Flow — drive safely!");
  }, []);

  const reportIssue = useCallback(() => {
    alert("Report a road issue — feature coming soon.");
  }, []);

  return (
    <div className="relative h-full w-full">
      <main className="absolute inset-0">
        <TrafficMap
          origin={origin}
          destination={destination}
          candidates={candidates}
          selectedRank={selectedRank}
          onMapClick={handleMapClick}
        />
      </main>

      <TopBar />

      <MapControls
        onCurrentLocation={locateMe}
        onReport={reportIssue}
      />

      <BottomSheet
        tab={tab}
        origin={origin}
        destination={destination}
        onOriginChange={onOriginChange}
        onDestinationChange={onDestinationChange}
        onOriginBlur={onOriginBlur}
        onDestinationBlur={onDestinationBlur}
        onOriginKeyDown={handleOriginKeyDown}
        onDestinationKeyDown={handleDestinationKeyDown}
        onSwap={swap}
        departureTime={departureTime}
        onDepartureChange={setDepartureTime}
        strategy={strategy}
        onStrategyChange={setStrategy}
        loading={loading}
        error={error}
        onRecommend={submit}
        candidates={candidates}
        selectedRank={selectedRank}
        onSelectRoute={setSelectedRank}
        onStartDrive={startDrive}
        onTabChange={(t) => {
          setTab(t);
          if (t === "input") {
            setCandidates([]);
            setSelectedRank(null);
          }
        }}
      />

      <footer className="absolute bottom-2 left-0 right-0 text-center text-xs text-slate-500">
        <span className="bg-white/80 backdrop-blur-sm px-2 py-0.5 rounded">
          NAIROBI FLOW · backend: <span className={healthClass}>{health}</span>
        </span>
      </footer>
    </div>
  );
}