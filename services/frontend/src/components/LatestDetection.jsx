import { useState } from "react";
import { formatTime } from "../utils/format";
import { IconAlertTriangle, IconUsers, IconMapPin } from "./Icon";

export default function LatestDetection({ detection, loading }) {
  const [imgFailed, setImgFailed] = useState(false);
  const hasData = detection && detection.type;

  return (
    <section className="panel">
      <h2 className="panel__title">Latest detection</h2>

      {!hasData && (
        <div className="panel__empty">
          {loading ? "Connecting to detection feed…" : "Waiting for the first detection…"}
        </div>
      )}

      {hasData && (
        <div className="latest-detection">
          {detection.image_url && !imgFailed && (
            <div className="latest-detection__image-wrap">
              <img
                src={detection.image_url}
                alt={`${detection.type} detection at ${detection.location}`}
                className="latest-detection__image"
                onError={() => setImgFailed(true)}
              />
              <span
                className={`latest-detection__badge ${
                  detection.threat ? "latest-detection__badge--threat" : "latest-detection__badge--safe"
                }`}
              >
                {detection.threat ? <IconAlertTriangle /> : <IconUsers />}
                {detection.type}
              </span>
            </div>
          )}

          <div className="latest-detection__meta">
            <ConfidenceRing value={detection.confidence} threat={detection.threat} />
            <div className="latest-detection__meta-grid">
              <div>
                <div className="meta-label">Detected at</div>
                <div className="meta-value meta-value--mono">{formatTime(detection.timestamp)}</div>
              </div>
              <div>
                <div className="meta-label">Count</div>
                <div className="meta-value meta-value--mono">{detection.count}</div>
              </div>
              <div className="latest-detection__meta-span">
                <div className="meta-label">
                  <IconMapPin /> Location &middot; classes
                </div>
                <div className="meta-value">
                  {detection.location} — {detection.classes?.join(", ")}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function ConfidenceRing({ value, threat }) {
  const pct = Math.round((value ?? 0) * 100);
  const color = threat ? "var(--status-bad)" : "var(--accent-cyan)";
  return (
    <div
      className="confidence-ring"
      style={{
        background: `conic-gradient(${color} ${pct * 3.6}deg, var(--border) 0deg)`,
      }}
      role="img"
      aria-label={`Confidence ${pct} percent`}
    >
      <div className="confidence-ring__inner">
        <span className="confidence-ring__value">{pct}%</span>
        <span className="confidence-ring__label">confidence</span>
      </div>
    </div>
  );
}
