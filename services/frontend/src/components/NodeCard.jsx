import { statusTone } from "../utils/format";
import { IconCpu, IconThermometer, IconClock } from "./Icon";

export default function NodeCard({ node }) {
  const cpuTone = statusTone(node.cpu_percent);
  const memTone = statusTone(node.memory_percent);
  const isReady = node.status === "Ready";

  return (
    <article className={`node-card ${node.role === "control-plane" ? "node-card--cp" : ""}`}>
      <header className="node-card__header">
        <div>
          <div className="node-card__name">{node.name}</div>
          <div className="node-card__meta">
            {node.role === "control-plane" ? "control-plane" : "worker"} &middot; {node.ip}
          </div>
        </div>
        <span className={`badge ${isReady ? "badge--good" : "badge--bad"}`}>{node.status}</span>
      </header>

      <MetricBar icon={IconCpu} label="CPU" value={node.cpu_percent} tone={cpuTone} />
      <MetricBar icon={IconCpu} label="Memory" value={node.memory_percent} tone={memTone} />

      <footer className="node-card__footer">
        <span>
          <IconThermometer /> {node.temperature}&deg;C
        </span>
        <span>
          <IconClock /> {node.uptime}
        </span>
      </footer>
    </article>
  );
}

function MetricBar({ icon: Icon, label, value, tone }) {
  return (
    <div className="metric-bar">
      <div className="metric-bar__row">
        <span className="metric-bar__label">
          <Icon /> {label}
        </span>
        <span className={`metric-bar__value metric-bar__value--${tone}`}>{value}%</span>
      </div>
      <div className="metric-bar__track">
        <div
          className={`metric-bar__fill metric-bar__fill--${tone}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
}
