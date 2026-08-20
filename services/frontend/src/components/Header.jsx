import { API_BASE } from "../api/client";
import { useClock } from "../hooks/useClock";
import { formatClock } from "../utils/format";
import { IconWifi, IconWifiOff } from "./Icon";

export default function Header({ isOnline }) {
  const now = useClock();

  return (
    <header className="header">
      <div className="header__brand">
        <span className="header__mark" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 20 20" fill="none">
            <path
              d="M10 2.2 17 4.6v5.1c0 4.4-3 7-7 8.1-4-1.1-7-3.7-7-8.1V4.6L10 2.2Z"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinejoin="round"
            />
            <circle cx="10" cy="9.5" r="2.4" stroke="currentColor" strokeWidth="1.6" />
          </svg>
        </span>
        <div>
          <h1 className="header__title">Edge Cluster Monitor</h1>
          <p className="header__subtitle">
            Group 8 &middot; Cloud Computing SS2026 &middot; Frankfurt UAS
          </p>
        </div>
      </div>

      <div className="header__status">
        <div className="header__clock" title="Local time">
          {formatClock(now)}
        </div>
        <div className={`status-pill ${isOnline ? "status-pill--good" : "status-pill--bad"}`}>
          {isOnline ? <IconWifi /> : <IconWifiOff />}
          <span>{isOnline ? "Live" : "Offline"}</span>
        </div>
        <div className="header__api" title="Backend endpoint this dashboard is polling">
          {API_BASE.replace(/^https?:\/\//, "")}
        </div>
      </div>
    </header>
  );
}
