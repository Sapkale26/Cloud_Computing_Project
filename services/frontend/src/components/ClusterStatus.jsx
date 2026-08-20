import NodeCard from "./NodeCard";
import { IconLayers } from "./Icon";

export default function ClusterStatus({ nodes, loading }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">
          <IconLayers /> Cluster status
        </h2>
        {nodes && (
          <span className="panel__count">
            {nodes.filter((n) => n.status === "Ready").length}/{nodes.length} ready
          </span>
        )}
      </div>

      <div className="node-grid">
        {!nodes && loading
          ? Array.from({ length: 8 }).map((_, i) => <div key={i} className="node-card skeleton skeleton--card" />)
          : nodes?.map((node) => <NodeCard key={node.name} node={node} />)}
      </div>
    </section>
  );
}
