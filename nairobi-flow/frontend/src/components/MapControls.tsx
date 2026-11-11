import { LocationIcon, ReportIcon } from "./icons";

export interface MapControlsProps {
  onCurrentLocation?: () => void;
  onReport?: () => void;
}

export default function MapControls({
  onCurrentLocation,
  onReport,
}: MapControlsProps) {
  return (
    <div className="absolute bottom-24 right-4 flex flex-col gap-3 z-50">
      <button
        type="button"
        onClick={onCurrentLocation}
        className="w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center active:scale-90 transition border border-slate-200"
        aria-label="Current location"
        title="My location"
      >
        <div className="relative w-5 h-5">
          <LocationIcon className="w-5 h-5 text-slate-800" />
          <div className="absolute -inset-0.5 rounded-full bg-emerald-500/20 animate-pulse" />
        </div>
      </button>

      <button
        type="button"
        onClick={onReport}
        className="w-12 h-12 rounded-full bg-amber-400 shadow-lg flex items-center justify-center active:scale-90 transition border border-amber-300"
        aria-label="Report"
        title="Report issue"
      >
        <ReportIcon className="w-5 h-5 text-slate-800" />
      </button>
    </div>
  );
}