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
    <div className="absolute bottom-32 right-4 flex flex-col gap-3 z-10">
      <button
        type="button"
        onClick={onCurrentLocation}
        className="w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center active:scale-90 transition"
        aria-label="Current location"
      >
        <LocationIcon className="w-5 h-5 text-slate-800" />
      </button>

      <button
        type="button"
        onClick={onReport}
        className="w-12 h-12 rounded-full bg-amber-400 shadow-lg flex items-center justify-center active:scale-90 transition"
        aria-label="Report"
      >
        <ReportIcon className="w-5 h-5 text-slate-800" />
      </button>
    </div>
  );
}