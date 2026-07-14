import { useState, useEffect, useRef } from "react";

const API = "http://192.168.50.1:5000";

function useApi(endpoint, interval = 5000) {
  const [data, setData] = useState(null);
  const ref = useRef(data);
  useEffect(() => {
    const fetch_ = () =>
      fetch(`${API}${endpoint}`)
        .then((r) => r.json())
        .then((d) => {
          ref.current = d;
          setData(d);
        })
        .catch(console.error);
    fetch_();
    const t = setInterval(fetch_, interval);
    return () => clearInterval(t);
  }, [endpoint]);
  return data;
}

function StatCard({ label, value, color }) {
  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: 12,
        padding: "16px 20px",
        flex: 1,
        minWidth: 120,
      }}
    >
      <div style={{ color: "#94a3b8", fontSize: 12, marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ color: color || "#f1f5f9", fontSize: 26, fontWeight: 700 }}>
        {value ?? "—"}
      </div>
    </div>
  );
}

function NodeCard({ node }) {
  const cpuColor =
    node.cpu_percent > 70
      ? "#ef4444"
      : node.cpu_percent > 40
        ? "#f59e0b"
        : "#22c55e";
  const memColor =
    node.memory_percent > 70
      ? "#ef4444"
      : node.memory_percent > 40
        ? "#f59e0b"
        : "#22c55e";
  const isWorker = node.role === "worker";
  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: 12,
        padding: 16,
        flex: 1,
        minWidth: 140,
        border: isWorker ? "1px solid #1e40af22" : "1px solid #374151",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 6,
        }}
      >
        <span style={{ color: "#f1f5f9", fontWeight: 600, fontSize: 13 }}>
          {node.name}
        </span>
        <span
          style={{
            background: node.status === "Ready" ? "#22c55e22" : "#ef444422",
            color: node.status === "Ready" ? "#22c55e" : "#ef4444",
            borderRadius: 6,
            padding: "2px 6px",
            fontSize: 10,
          }}
        >
          {node.status}
        </span>
      </div>
      <div style={{ color: "#64748b", fontSize: 10, marginBottom: 8 }}>
        {node.role} • {node.ip}
      </div>
      {["cpu", "memory"].map((type) => {
        const val = type === "cpu" ? node.cpu_percent : node.memory_percent;
        const color = type === "cpu" ? cpuColor : memColor;
        return (
          <div key={type} style={{ marginBottom: 6 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 11,
                color: "#94a3b8",
                marginBottom: 3,
              }}
            >
              <span>{type.toUpperCase()}</span>
              <span style={{ color }}>{val}%</span>
            </div>
            <div style={{ background: "#0f172a", borderRadius: 4, height: 5 }}>
              <div
                style={{
                  background: color,
                  width: `${Math.min(val, 100)}%`,
                  height: "100%",
                  borderRadius: 4,
                  transition: "width 1s ease",
                }}
              />
            </div>
          </div>
        );
      })}
      <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
        🌡️ {node.temperature}°C • ⏱️ {node.uptime}
      </div>
    </div>
  );
}

export default function App() {
  const stats = useApi("/api/stats", 5000);
  const latest = useApi("/api/detections/latest", 1);
  const clusterData = useApi("/api/cluster/nodes", 8000);
  const alertData = useApi("/api/alerts", 5000);
  const detectionsData = useApi("/api/detections", 5000);

  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        color: "#f1f5f9",
        fontFamily: "Inter, system-ui, sans-serif",
        padding: "16px 20px",
        boxSizing: "border-box",
        width: "100%",
        maxWidth: "100%",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>
            🖥️ Edge Computing Monitor
          </h1>
          <div style={{ color: "#64748b", fontSize: 12 }}>
            Cloud Computing SS2026 — Frankfurt UAS
          </div>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "#1e293b",
            borderRadius: 8,
            padding: "6px 12px",
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#22c55e",
              display: "inline-block",
              animation: "pulse 2s infinite",
            }}
          />
          <span style={{ fontSize: 12 }}>Live</span>
        </div>
      </div>

      {/* Stats Row */}
      <div
        style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}
      >
        <StatCard
          label="Detections Today"
          value={stats?.total_detections_today}
          color="#60a5fa"
        />
        <StatCard
          label="People Detected"
          value={stats?.total_people_detected}
          color="#a78bfa"
        />
        <StatCard
          label="Threats"
          value={stats?.total_threats_detected}
          color="#ef4444"
        />
        <StatCard
          label="Accuracy"
          value={stats ? `${stats.detection_accuracy}%` : null}
          color="#22c55e"
        />
        <StatCard
          label="Active Nodes"
          value={stats ? `${stats.active_nodes}/${stats.total_nodes}` : null}
          color="#f59e0b"
        />
      </div>

      {/* Main Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 16,
          marginBottom: 16,
        }}
      >
        {/* Latest Detection */}
        <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
          <h2
            style={{
              margin: "0 0 12px",
              fontSize: 14,
              color: "#94a3b8",
              fontWeight: 600,
            }}
          >
            🎯 Latest Detection
          </h2>
          {latest && latest.type ? (
            <div>
              {latest.image_url && (
                <img
                  src={latest.image_url}
                  alt="detection"
                  style={{
                    width: "100%",
                    borderRadius: 8,
                    marginBottom: 12,
                    objectFit: "cover",
                    maxHeight: 200,
                  }}
                  onError={(e) => (e.target.style.display = "none")}
                />
              )}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 10,
                }}
              >
                <span style={{ fontSize: 30 }}>
                  {latest.threat ? "⚠️" : "👤"}
                </span>
                <div>
                  <div
                    style={{
                      fontSize: 18,
                      fontWeight: 700,
                      color: latest.threat ? "#ef4444" : "#60a5fa",
                      textTransform: "capitalize",
                    }}
                  >
                    {latest.type}
                  </div>
                  <div style={{ color: "#64748b", fontSize: 12 }}>
                    {new Date(latest.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 8,
                }}
              >
                <div
                  style={{
                    background: "#0f172a",
                    borderRadius: 8,
                    padding: 10,
                  }}
                >
                  <div style={{ color: "#64748b", fontSize: 11 }}>
                    Confidence
                  </div>
                  <div
                    style={{ color: "#f1f5f9", fontSize: 16, fontWeight: 600 }}
                  >
                    {Math.round(latest.confidence * 100)}%
                  </div>
                </div>
                <div
                  style={{
                    background: "#0f172a",
                    borderRadius: 8,
                    padding: 10,
                  }}
                >
                  <div style={{ color: "#64748b", fontSize: 11 }}>Count</div>
                  <div
                    style={{ color: "#f1f5f9", fontSize: 16, fontWeight: 600 }}
                  >
                    {latest.count}
                  </div>
                </div>
                <div
                  style={{
                    background: "#0f172a",
                    borderRadius: 8,
                    padding: 10,
                    gridColumn: "span 2",
                  }}
                >
                  <div style={{ color: "#64748b", fontSize: 11 }}>
                    Location • Classes
                  </div>
                  <div
                    style={{ color: "#f1f5f9", fontSize: 13, fontWeight: 600 }}
                  >
                    {latest.location} — {latest.classes?.join(", ")}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: "#64748b" }}>Waiting for detections...</div>
          )}
        </div>

        {/* Alerts */}
        <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
          <h2
            style={{
              margin: "0 0 12px",
              fontSize: 14,
              color: "#94a3b8",
              fontWeight: 600,
            }}
          >
            🔔 Alerts
          </h2>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 8,
              maxHeight: 320,
              overflowY: "auto",
            }}
          >
            {alertData?.alerts?.length > 0 ? (
              alertData.alerts.map((a) => (
                <div
                  key={a.id}
                  style={{
                    background: "#0f172a",
                    borderRadius: 8,
                    padding: "10px 14px",
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    opacity: a.acknowledged ? 0.5 : 1,
                    borderLeft: `3px solid ${a.severity === "high" ? "#ef4444" : "#f59e0b"}`,
                  }}
                >
                  <span style={{ fontSize: 16 }}>
                    {a.severity === "high" ? "🔴" : "🟡"}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: "#f1f5f9", fontSize: 12 }}>
                      {a.message}
                    </div>
                    <div style={{ color: "#64748b", fontSize: 10 }}>
                      {new Date(a.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  {a.acknowledged && (
                    <span style={{ color: "#22c55e", fontSize: 10 }}>
                      ✓ ACK
                    </span>
                  )}
                </div>
              ))
            ) : (
              <div style={{ color: "#64748b", fontSize: 13 }}>No alerts</div>
            )}
          </div>
        </div>
      </div>

      {/* Cluster Status */}
      <div
        style={{
          background: "#1e293b",
          borderRadius: 12,
          padding: 16,
          marginBottom: 16,
        }}
      >
        <h2
          style={{
            margin: "0 0 12px",
            fontSize: 14,
            color: "#94a3b8",
            fontWeight: 600,
          }}
        >
          🖧 Cluster Status
        </h2>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {clusterData?.nodes?.map((n) => (
            <NodeCard key={n.name} node={n} />
          )) ?? <div style={{ color: "#64748b" }}>Loading...</div>}
        </div>
      </div>

      {/* Recent Detections */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
        <h2
          style={{
            margin: "0 0 12px",
            fontSize: 14,
            color: "#94a3b8",
            fontWeight: 600,
          }}
        >
          📋 Recent Detections
        </h2>
        <div style={{ overflowX: "auto" }}>
          <table
            style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}
          >
            <thead>
              <tr
                style={{
                  color: "#64748b",
                  textAlign: "left",
                  borderBottom: "1px solid #0f172a",
                }}
              >
                <th style={{ padding: "8px 10px" }}>Time</th>
                <th style={{ padding: "8px 10px" }}>Type</th>
                <th style={{ padding: "8px 10px" }}>Classes</th>
                <th style={{ padding: "8px 10px" }}>Count</th>
                <th style={{ padding: "8px 10px" }}>Confidence</th>
                <th style={{ padding: "8px 10px" }}>Location</th>
                <th style={{ padding: "8px 10px" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {detectionsData?.detections?.map((d) => (
                <tr key={d.id} style={{ borderTop: "1px solid #0f172a" }}>
                  <td style={{ padding: "8px 10px", color: "#94a3b8" }}>
                    {new Date(d.timestamp).toLocaleTimeString()}
                  </td>
                  <td
                    style={{
                      padding: "8px 10px",
                      textTransform: "capitalize",
                      color: d.threat ? "#ef4444" : "#60a5fa",
                    }}
                  >
                    {d.type}
                  </td>
                  <td style={{ padding: "8px 10px", color: "#94a3b8" }}>
                    {d.classes?.join(", ")}
                  </td>
                  <td style={{ padding: "8px 10px" }}>{d.count}</td>
                  <td style={{ padding: "8px 10px" }}>
                    {Math.round(d.confidence * 100)}%
                  </td>
                  <td style={{ padding: "8px 10px", color: "#94a3b8" }}>
                    {d.location}
                  </td>
                  <td style={{ padding: "8px 10px" }}>
                    <span
                      style={{
                        background: d.threat ? "#ef444422" : "#22c55e22",
                        color: d.threat ? "#ef4444" : "#22c55e",
                        borderRadius: 6,
                        padding: "2px 6px",
                        fontSize: 10,
                      }}
                    >
                      {d.threat ? "⚠️ Threat" : "✅ Safe"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
