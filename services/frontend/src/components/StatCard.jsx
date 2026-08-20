export default function StatCard({ label, value, icon: Icon, tone = "cyan", loading }) {
  return (
    <div className={`stat-card stat-card--${tone}`}>
      <div className="stat-card__icon" aria-hidden="true">
        <Icon />
      </div>
      <div className="stat-card__body">
        <div className="stat-card__label">{label}</div>
        <div className="stat-card__value">
          {loading && value === null ? <span className="skeleton skeleton--text" /> : value ?? "—"}
        </div>
      </div>
    </div>
  );
}
