import { useCallback } from "react";
import type { LonLat, RouteCandidate, Strategy } from "../types";
import { ChevronDownIcon, SwapIcon } from "./icons";

export type BottomSheetTab = "input" | "routes";

export interface BottomSheetProps {
  tab: BottomSheetTab;
  origin: LonLat | null;
  destination: LonLat | null;
  onOriginChange: (v: string) => void;
  onDestinationChange: (v: string) => void;
  onOriginBlur: () => void;
  onDestinationBlur: () => void;
  onOriginKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  onDestinationKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  onSwap: () => void;
  onReDetectLocation: () => void;
  departureTime: string;
  onDepartureChange: (v: string) => void;
  strategy: Strategy;
  onStrategyChange: (v: Strategy) => void;
  loading: boolean;
  error: string | null;
  onRecommend: () => void;
  candidates: RouteCandidate[];
  selectedRank: number | null;
  onSelectRoute: (rank: number) => void;
  onStartDrive: () => void;
  onTabChange: (tab: BottomSheetTab) => void;
}

const ROUTE_COLORS = ["#38bdf8", "#a78bfa", "#f472b6", "#fbbf24"];

export default function BottomSheet({
  tab,
  origin,
  destination,
  onOriginChange,
  onDestinationChange,
  onOriginBlur,
  onDestinationBlur,
  onOriginKeyDown,
  onDestinationKeyDown,
  onSwap,
  onReDetectLocation,
  departureTime,
  onDepartureChange,
  strategy,
  onStrategyChange,
  loading,
  error,
  onRecommend,
  candidates,
  selectedRank,
  onSelectRoute,
  onStartDrive,
  onTabChange,
}: BottomSheetProps) {
  const handleGrab = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      const clientY =
        "touches" in e ? e.touches[0]?.clientY : (e as React.MouseEvent).clientY;
      if (clientY && clientY > 100 && tab === "routes") {
        onTabChange("input");
      }
    },
    [onTabChange, tab],
  );

  const inputDisabled = !origin || !destination;
  const hasRouteResults = candidates.length > 0;

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl flex flex-col max-h-[55vh] z-10 transition-all duration-300">
      <div
        className="w-10 h-1.5 bg-slate-200 rounded-full self-center mt-2 cursor-row-resize"
        onMouseDown={handleGrab}
        onTouchStart={handleGrab}
      />

      {tab === "input" && (
        <>
          <div className="px-5 py-4 border-b border-slate-100">
            <h2 className="text-base font-semibold text-slate-800">
              Route request
            </h2>
          </div>

          <div className="px-5 py-4 space-y-4 overflow-y-auto flex-1">
            <div className="space-y-3">
              <div>
                <label className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                  <MapPinIcon className="w-4 h-4 text-emerald-500" />
                  Origin
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Tap map or enter lon, lat"
                    className="flex-1 h-12 rounded-xl bg-slate-50 border border-slate-200 px-3 text-sm font-mono text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:bg-white"
                    value={origin ? `${origin[0].toFixed(4)}, ${origin[1].toFixed(4)}` : ""}
                    onChange={(e) => onOriginChange(e.target.value)}
                    onBlur={onOriginBlur}
                    onKeyDown={onOriginKeyDown}
                  />
                  <button
                    type="button"
                    onClick={onReDetectLocation}
                    className="h-12 rounded-xl bg-white border border-slate-200 px-3 flex items-center justify-center text-sm text-sky-600 font-medium hover:bg-sky-50 active:scale-95 transition"
                    aria-label="Re-detect my location"
                  >
                    📍
                  </button>
                </div>
              </div>

              <div className="flex justify-center -my-1">
                <button
                  type="button"
                  onClick={onSwap}
                  disabled={!origin && !destination}
                  className="w-9 h-9 rounded-full bg-sky-100 flex items-center justify-center disabled:opacity-40 active:scale-95 transition"
                  aria-label="Swap"
                >
                  <SwapIcon className="w-4 h-4 text-sky-700" />
                </button>
              </div>

              <div>
                <label className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                  <MapPinIcon className="w-4 h-4 text-red-500" />
                  Destination
                </label>
                <input
                  type="text"
                  placeholder="Tap map or enter lon, lat"
                  className="w-full h-12 rounded-xl bg-slate-50 border border-slate-200 px-3 text-sm font-mono text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:bg-white"
                  value={destination ? `${destination[0].toFixed(4)}, ${destination[1].toFixed(4)}` : ""}
                  onChange={(e) => onDestinationChange(e.target.value)}
                  onBlur={onDestinationBlur}
                  onKeyDown={onDestinationKeyDown}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs text-slate-500 mb-1">
                Departure
              </label>
              <input
                type="datetime-local"
                className="w-full h-12 rounded-xl bg-slate-50 border border-slate-200 px-3 text-sm text-slate-800 focus:outline-none focus:border-sky-400 focus:bg-white"
                value={departureTime}
                onChange={(e) => onDepartureChange(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs text-slate-500 mb-1">
                Strategy
              </label>
              <select
                className="w-full h-12 rounded-xl bg-slate-50 border border-slate-200 px-3 text-sm text-slate-800 focus:outline-none focus:border-sky-400"
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
            </div>

            {error && <p className="text-xs text-rose-500">{error}</p>}
          </div>

          <button
            type="button"
            onClick={onRecommend}
            disabled={inputDisabled || loading}
            className="mx-5 my-3 h-13 rounded-full bg-sky-500 hover:bg-sky-400 disabled:bg-slate-300 disabled:text-slate-400 text-white font-semibold text-base active:scale-[0.98] transition"
          >
            {loading ? "Routing…" : "Recommend Routes"}
          </button>
        </>
      )}

      {tab === "routes" && hasRouteResults && (
        <>
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-800">
              Recommended routes
            </h2>
            <button
              type="button"
              onClick={() => onTabChange("input")}
              className="p-1 text-slate-500 active:scale-90 transition"
              aria-label="Back to input"
            >
              <ChevronDownIcon className="w-5 h-5 rotate-180" />
            </button>
          </div>

          <div className="px-5 py-3 space-y-3 overflow-y-auto flex-1">
            {candidates.map((c) => {
              const isSelected = c.rank === selectedRank;
              return (
                <button
                  key={c.rank}
                  type="button"
                  onClick={() => onSelectRoute(c.rank)}
                  className={`w-full rounded-2xl border-2 p-4 text-left transition-all ${
                    isSelected
                      ? "border-sky-500 bg-sky-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-slate-800">
                      Route {c.rank + 1}
                    </span>
                    <span
                      className="inline-block w-3 h-3 rounded-full"
                      style={{
                        backgroundColor:
                          ROUTE_COLORS[c.rank % ROUTE_COLORS.length],
                      }}
                    />
                  </div>
                  <div className="text-sm text-slate-600">
                    {fmtDuration(c.current_travel_time_s)} ·{" "}
                    {fmtDistance(c.distance_m)}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Risk: {c.risk_level}
                  </div>
                </button>
              );
            })}
          </div>

          <button
            type="button"
            onClick={onStartDrive}
            className="mx-5 my-4 h-13 rounded-full bg-sky-500 hover:bg-sky-400 text-white font-semibold text-base active:scale-[0.98] transition"
          >
            Start Drive
          </button>
        </>
      )}
    </div>
  );
}

function MapPinIcon({ className }: { className: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M21 10c0 6-9 13-9 13s-9-7-9-13a9 9 0 0 1 18 0z" />
      <circle cx={12} cy={10} r={3} />
    </svg>
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
