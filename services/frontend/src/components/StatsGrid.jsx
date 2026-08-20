import StatCard from "./StatCard";
import {
  IconActivity,
  IconUsers,
  IconAlertTriangle,
  IconShieldCheck,
  IconServer,
} from "./Icon";

export default function StatsGrid({ stats, loading }) {
  return (
    <section className="stats-grid" aria-label="Key metrics">
      <StatCard
        label="Detections today"
        value={stats?.total_detections_today}
        icon={IconActivity}
        tone="cyan"
        loading={loading}
      />
      <StatCard
        label="People detected"
        value={stats?.total_people_detected}
        icon={IconUsers}
        tone="violet"
        loading={loading}
      />
      <StatCard
        label="Threats flagged"
        value={stats?.total_threats_detected}
        icon={IconAlertTriangle}
        tone="red"
        loading={loading}
      />
      <StatCard
        label="Detection accuracy"
        value={stats ? `${stats.detection_accuracy}%` : null}
        icon={IconShieldCheck}
        tone="green"
        loading={loading}
      />
      <StatCard
        label="Active nodes"
        value={stats ? `${stats.active_nodes}/${stats.total_nodes}` : null}
        icon={IconServer}
        tone="amber"
        loading={loading}
      />
    </section>
  );
}
