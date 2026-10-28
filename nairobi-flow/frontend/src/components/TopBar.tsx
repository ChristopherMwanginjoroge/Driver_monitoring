import { MenuIcon, ProfileIcon, SearchIcon } from "./icons";

export interface TopBarProps {
  onSearchFocus?: () => void;
}

export default function TopBar({ onSearchFocus }: TopBarProps) {
  return (
    <header className="absolute top-0 left-0 right-0 flex items-center justify-between px-4 py-3 z-10">
      <button
        type="button"
        className="w-10 h-10 rounded-full bg-white/90 flex items-center justify-center shadow-md active:scale-95 transition-transform"
        aria-label="Menu"
      >
        <MenuIcon className="w-5 h-5 text-slate-800" />
      </button>

      <button
        type="button"
        onClick={onSearchFocus}
        className="flex-1 mx-3 h-11 rounded-full bg-white/90 shadow-md flex items-center gap-2 px-4 text-slate-500 text-sm"
      >
        <SearchIcon className="w-4 h-4" />
        <span>Where to?</span>
      </button>

      <button
        type="button"
        className="w-10 h-10 rounded-full bg-white/90 flex items-center justify-center shadow-md active:scale-95 transition-transform"
        aria-label="Profile"
      >
        <ProfileIcon className="w-5 h-5 text-slate-800" />
      </button>
    </header>
  );
}