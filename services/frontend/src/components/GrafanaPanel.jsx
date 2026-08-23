const GRAFANA_URL =
  import.meta.env.VITE_GRAFANA_URL ||
  "http://192.168.50.1:3000/d/rYdddlPWk/node-exporter-full?orgId=1&refresh=30s&kiosk=tv";

export default function GrafanaPanel() {
  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Cluster monitoring (Grafana)</h2>
      </div>
      <div className="grafana-panel__frame-wrap">
        <iframe
          src={GRAFANA_URL}
          title="Grafana — Node Exporter Full"
          className="grafana-panel__frame"
          loading="lazy"
        />
      </div>
    </section>
  );
}
