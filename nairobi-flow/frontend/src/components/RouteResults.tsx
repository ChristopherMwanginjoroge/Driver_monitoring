import type { RouteCandidate } from "../types";

const ROUTE_COLORS = ["#38bdf8", "#a78bfa", "#f472b6", "#fbbf24"];

export interface RouteResultsProps {
  candidates: RouteCandidate[];
  selectedRank: number | null;
  onSelect: (rank: number) => void;
}

export default function RouteResults({
  candidates,
  selectedRank,
  onSelect,
}: RouteResultsProps) {
  if (candidates.length === 0) return null;

  return (
    <section className="space-y-2">
      <h2 className="text-sm uppercase tracking-wide text-slate-400">
        Candidates
      </h2>
      <ul className="space-y-2">
        {candidates.map((c) => {
          const isSelected = c.rank === selectedRank;
          const color = ROUTE_COLORS[c.rank % ROUTE_COLORS.length];
          return (
            <li key={c.rank}>
              <button
                type="button"
                onClick={() => onSelect(c.rank)}
                className={`w-full text-left rounded border px-3 py-2 text-sm space-y-1 transition ${
                  isSelected
                    ? "border-sky-500 bg-slate-800"
                    : "border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block w-3 h-3 rounded-sm"
                    style={{ backgroundColor: color }}
                  />
                  <span className="font-semibold">Route {c.rank + 1}</span>
                  <span className="ml-auto text-slate-400 text-xs">
                    {fmtDuration(c.current_travel_time_s)} ·{" "}
                    {fmtDistance(c.distance_m)}
                  </span>
                </div>
                <div className="text-xs text-slate-400">
                  risk: {c.risk_level}
                </div>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

function fmtDuration(seconds: number): string {
  const m = Math.round(seconds / 60);
  if (m < 60) return `${m} min`;
  const h = Math.floor(m / 60);
  return `${h}h ${m - h * 60}m`;
}

function fmtDistance(m: number): string {
  if (m < 1000) return `${Math.round(m)} m`;
  return `${(m / 1000).toFixed(1)} km`;
}
