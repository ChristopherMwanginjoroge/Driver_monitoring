import { useMemo } from "react";
import type { LonLat, Strategy } from "../types";

export interface RouteFormProps {
  origin: LonLat | null;
  destination: LonLat | null;
  strategy: Strategy;
  departureTime: string;
  loading: boolean;
  error: string | null;
  onStrategyChange: (s: Strategy) => void;
  onDepartureChange: (iso: string) => void;
  onClearPoints: () => void;
  onSwap: () => void;
  onUsePreset: () => void;
  onSubmit: () => void;
}

export default function RouteForm(props: RouteFormProps) {
  const {
    origin,
    destination,
    strategy,
    departureTime,
    loading,
    error,
    onStrategyChange,
    onDepartureChange,
    onClearPoints,
    onSwap,
    onUsePreset,
    onSubmit,
  } = props;

  const canSubmit = useMemo(
    () => !!origin && !!destination && !loading,
    [origin, destination, loading],
  );

  return (
    <section className="space-y-3">
      <h2 className="text-sm uppercase tracking-wide text-slate-400">
        Route request
      </h2>

      <div className="text-xs space-y-1">
        <PointRow label="Origin" point={origin} color="bg-emerald-500" />
        <PointRow label="Destination" point={destination} color="bg-rose-500" />
        <p className="text-slate-500 pt-1 flex gap-3">
          <button className="underline hover:text-slate-300" onClick={onUsePreset} type="button">
            Rongai → CBD preset
          </button>
          <button className="underline hover:text-slate-300" onClick={onSwap} type="button">
            swap
          </button>
          <button className="underline hover:text-slate-300" onClick={onClearPoints} type="button">
            clear
          </button>
        </p>
      </div>

      <label className="block text-xs">
        <span className="text-slate-400 uppercase tracking-wide">Departure</span>
        <input
          type="datetime-local"
          className="mt-1 w-full rounded bg-slate-800 border border-slate-700 px-2 py-1 text-sm"
          value={departureTime}
          onChange={(e) => onDepartureChange(e.target.value)}
        />
      </label>

      <label className="block text-xs">
        <span className="text-slate-400 uppercase tracking-wide">Strategy</span>
        <select
          className="mt-1 w-full rounded bg-slate-800 border border-slate-700 px-2 py-1 text-sm"
          value={strategy}
          onChange={(e) => onStrategyChange(e.target.value as Strategy)}
        >
          <option value="conventional">Conventional</option>
          <option value="predictive" disabled>
            Predictive (needs trained model)
          </option>
          <option value="network_aware" disabled>
            Network-aware (needs assignment loop)
          </option>
        </select>
      </label>

      <button
        type="button"
        onClick={onSubmit}
        disabled={!canSubmit}
        className="w-full rounded bg-sky-500 hover:bg-sky-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-950 font-semibold py-2 text-sm"
      >
        {loading ? "Routing…" : "Recommend routes"}
      </button>

      {error && (
        <p className="text-xs text-rose-400 border border-rose-900/60 bg-rose-950/40 rounded px-2 py-1">
          {error}
        </p>
      )}

      <p className="text-xs text-slate-500">
        Tip: click the map once to set the origin, click again for the
        destination. Subsequent clicks replace the destination.
      </p>
    </section>
  );
}

function PointRow({
  label,
  point,
  color,
}: {
  label: string;
  point: LonLat | null;
  color: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className={`inline-block w-2 h-2 rounded-full ${color}`} />
      <span className="text-slate-400 w-20">{label}</span>
      <span className="font-mono">
        {point ? `${point[0].toFixed(4)}, ${point[1].toFixed(4)}` : (
          <span className="text-slate-600">click map</span>
        )}
      </span>
    </div>
  );
}

