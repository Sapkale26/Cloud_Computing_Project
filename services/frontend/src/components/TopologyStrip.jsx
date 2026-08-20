import { statusTone } from "../utils/format";

/**
 * A literal, compact read-out of the physical cluster: one chip per node,
 * colored by health. This stands in for the usual "big hero number" —
 * it's the actual thing being monitored, glanceable in under a second.
 */
export default function TopologyStrip({ nodes, loading }) {
  const skeletonCount = 8;

  return (
    <section className="topology" aria-label="Cluster topology at a glance">
      <div className="topology__label">
        <span>Cluster topology</span>
        {nodes && (
          <span className="topology__count">
            {nodes.filter((n) => n.status === "Ready").length}/{nodes.length} online
          </span>
        )}
      </div>
      <div className="topology__strip">
        {loading && !nodes
          ? Array.from({ length: skeletonCount }).map((_, i) => (
              <div key={i} className="topology__chip topology__chip--skeleton" />
            ))
          : nodes?.map((node) => {
              const isReady = node.status === "Ready";
              const tone = !isReady ? "bad" : statusTone(node.cpu_percent);
              return (
                <div
                  key={node.name}
                  className={`topology__chip topology__chip--${tone}`}
                  title={`${node.name} · ${node.role} · ${node.status} · CPU ${node.cpu_percent}%`}
                >
                  <span className="topology__chip-role">
                    {node.role === "control-plane" ? "CP" : "W"}
                  </span>
                  <span className="topology__chip-name">{node.name}</span>
                </div>
              );
            })}
      </div>
    </section>
  );
}
