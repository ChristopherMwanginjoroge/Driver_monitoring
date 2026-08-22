import { useCallback, useEffect, useMemo, useState } from "react";
import TrafficMap from "./components/TrafficMap";
import RouteForm from "./components/RouteForm";
import RouteResults from "./components/RouteResults";
import { fetchHealth, recommendRoute } from "./api/client";
import type { LonLat, RouteCandidate, Strategy } from "./types";

const RONGAI: LonLat = [36.7488, -1.3919];
const CBD: LonLat = [36.8172, -1.2864];

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

  useEffect(() => {
    fetchHealth()
      .then((h) => setHealth(h.status))
      .catch(() => setHealth("unreachable"));
  }, []);

  const handleMapClick = useCallback(
    (p: LonLat) => {
      if (!origin) setOrigin(p);
      else setDestination(p);
    },
    [origin],
  );

  const clearPoints = useCallback(() => {
    setOrigin(null);
    setDestination(null);
    setCandidates([]);
    setSelectedRank(null);
    setError(null);
  }, []);

  const swap = useCallback(() => {
    setOrigin(destination);
    setDestination(origin);
  }, [origin, destination]);

  const usePreset = useCallback(() => {
    setOrigin(RONGAI);
    setDestination(CBD);
    setCandidates([]);
    setSelectedRank(null);
    setError(null);
  }, []);

  const submit = useCallback(async () => {
    if (!origin || !destination) return;
    setLoading(true);
    setError(null);
    try {
      const iso = localToIso(departureTime);
      const res = await recommendRoute({
        origin,
        destination,
        departure_time: iso,
        strategy,
      });
      setCandidates(res.candidates);
      setSelectedRank(res.candidates[0]?.rank ?? null);
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

  return (
    <div className="flex h-full">
      <aside className="w-96 shrink-0 border-r border-slate-800 p-4 space-y-6 overflow-y-auto">
        <header>
          <h1 className="text-xl font-semibold">NAIROBI FLOW</h1>
          <p className="text-xs text-slate-400">
            Traffic intelligence · Rongai → CBD MVP
          </p>
          <p className="text-xs mt-2">
            <span className="text-slate-500">backend:</span>{" "}
            <span className={healthClass}>{health}</span>
          </p>
        </header>

        <RouteForm
          origin={origin}
          destination={destination}
          strategy={strategy}
          departureTime={departureTime}
          loading={loading}
          error={error}
          onStrategyChange={setStrategy}
          onDepartureChange={setDepartureTime}
          onClearPoints={clearPoints}
          onSwap={swap}
          onUsePreset={usePreset}
          onSubmit={submit}
        />

        <RouteResults
          candidates={candidates}
          selectedRank={selectedRank}
          onSelect={setSelectedRank}
        />
      </aside>

      <main className="flex-1 relative">
        <TrafficMap
          origin={origin}
          destination={destination}
          candidates={candidates}
          selectedRank={selectedRank}
          onMapClick={handleMapClick}
        />
      </main>
    </div>
  );
}

function defaultDepartureLocal(): string {
  const now = new Date();
  now.setSeconds(0, 0);
  const tzOffsetMs = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - tzOffsetMs).toISOString().slice(0, 16);
}

function localToIso(local: string): string {
  // `datetime-local` inputs have no zone; treat as local time and emit ISO
  // with the browser's current UTC offset.
  return new Date(local).toISOString();
}
