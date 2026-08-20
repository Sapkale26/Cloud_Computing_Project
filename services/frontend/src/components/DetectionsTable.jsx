import { useMemo, useState } from "react";
import { formatTime } from "../utils/format";
import { IconSearch } from "./Icon";

const FILTERS = [
  { id: "all", label: "All" },
  { id: "threat", label: "Threats" },
  { id: "person", label: "People" },
];

export default function DetectionsTable({ detections, loading }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");

  const rows = detections?.detections ?? [];

  const filtered = useMemo(() => {
    return rows.filter((d) => {
      if (filter === "threat" && !d.threat) return false;
      if (filter === "person" && d.threat) return false;
      if (!query.trim()) return true;
      const haystack = `${d.location} ${d.classes?.join(" ")} ${d.type}`.toLowerCase();
      return haystack.includes(query.trim().toLowerCase());
    });
  }, [rows, filter, query]);

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Recent detections</h2>
        <div className="table-controls">
          <div className="search-input">
            <IconSearch />
            <input
              type="search"
              placeholder="Search location or class…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search detections"
            />
          </div>
          <div className="filter-tabs" role="tablist" aria-label="Filter detections">
            {FILTERS.map((f) => (
              <button
                key={f.id}
                role="tab"
                aria-selected={filter === f.id}
                className={`filter-tab ${filter === f.id ? "filter-tab--active" : ""}`}
                onClick={() => setFilter(f.id)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Type</th>
              <th>Classes</th>
              <th>Count</th>
              <th>Confidence</th>
              <th>Location</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="data-table__empty">
                  {loading ? "Loading detections…" : "No detections match this view."}
                </td>
              </tr>
            )}
            {filtered.map((d) => (
              <tr key={d.id} className={d.threat ? "data-table__row--threat" : ""}>
                <td className="mono">{formatTime(d.timestamp)}</td>
                <td className="capitalize">{d.type}</td>
                <td className="text-muted">{d.classes?.join(", ")}</td>
                <td className="mono">{d.count}</td>
                <td className="mono">{Math.round(d.confidence * 100)}%</td>
                <td className="text-muted">{d.location}</td>
                <td>
                  <span className={`badge ${d.threat ? "badge--bad" : "badge--good"}`}>
                    {d.threat ? "Threat" : "Safe"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
