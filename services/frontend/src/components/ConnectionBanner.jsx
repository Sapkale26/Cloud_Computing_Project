import { API_BASE } from "../api/client";
import { IconAlertTriangle } from "./Icon";

export default function ConnectionBanner({ visible }) {
  if (!visible) return null;
  return (
    <div className="connection-banner" role="alert">
      <IconAlertTriangle />
      <span>
        Can&rsquo;t reach the backend at <code>{API_BASE}</code>. Showing the last known data while retrying…
      </span>
    </div>
  );
}
