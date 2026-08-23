import "./App.css";
import { useApi } from "./hooks/useApi";
import Header from "./components/Header";
import ConnectionBanner from "./components/ConnectionBanner";
import TopologyStrip from "./components/TopologyStrip";
import StatsGrid from "./components/StatsGrid";
import LatestDetection from "./components/LatestDetection";
import AlertsPanel from "./components/AlertsPanel";
import ClusterStatus from "./components/ClusterStatus";
import GrafanaPanel from "./components/GrafanaPanel";
import DetectionsTable from "./components/DetectionsTable";
import Footer from "./components/Footer";

export default function App() {
  const statsQuery = useApi("/api/stats", 5000);
  const latestQuery = useApi("/api/detections/latest", 3000);
  const clusterQuery = useApi("/api/cluster/nodes", 8000);
  const alertsQuery = useApi("/api/alerts", 5000);
  const detectionsQuery = useApi("/api/detections", 5000);

  const anyError = [statsQuery, latestQuery, clusterQuery, alertsQuery, detectionsQuery].some((q) => q.error);

  return (
    <div className="dashboard">
      <Header isOnline={!anyError} />
      <ConnectionBanner visible={anyError} />

      <TopologyStrip nodes={clusterQuery.data?.nodes} loading={clusterQuery.loading} />

      <StatsGrid stats={statsQuery.data} loading={statsQuery.loading} />

      <div className="main-grid">
        <LatestDetection detection={latestQuery.data} loading={latestQuery.loading} />
        <AlertsPanel alerts={alertsQuery.data} loading={alertsQuery.loading} />
      </div>

      <ClusterStatus nodes={clusterQuery.data?.nodes} loading={clusterQuery.loading} />

      <GrafanaPanel />

      <DetectionsTable detections={detectionsQuery.data} loading={detectionsQuery.loading} />

      <Footer />
    </div>
  );
}
