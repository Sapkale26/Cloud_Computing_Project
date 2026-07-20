import { useState, useEffect, useRef, useCallback } from "react";

const API = "http://192.168.50.1:5000";
const WS_URL = "ws://192.168.50.1:5001";

// ── Custom Hook: REST polling ─────────────────────────────
function useApi(endpoint, interval = 5000) {
  const [data, setData] = useState(null);
  useEffect(() => {
    const fetchData = () =>
      fetch(`${API}${endpoint}`)
        .then(r => r.json())
        .then(setData)
        .catch(console.error);
    fetchData();
    const t = setInterval(fetchData, interval);
    return () => clearInterval(t);
  }, [endpoint, interval]);
  return data;
}

// ── Custom Hook: WebSocket ────────────────────────────────
function useWebSocket() {
  const [liveFrame, setLiveFrame] = useState(null);
  const [liveDetection, setLiveDetection] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket(WS_URL);
      ws.current.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'frame') setLiveFrame(msg.frame);
        if (msg.type === 'detection') setLiveDetection(msg.data);
      };
      ws.current.onclose = () => setTimeout(connect, 3000);
    };
    connect();
    return () => ws.current?.close();
  }, []);

  return { liveFrame, liveDetection };
}

// ── Stat Card ─────────────────────────────────────────────
function StatCard({ label, value, color, icon }) {
  return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: "14px 18px", flex: 1, minWidth: 110 }}>
      <div style={{ color: "#94a3b8", fontSize: 11, marginBottom: 4 }}>{icon} {label}</div>
      <div style={{ color: color || "#f1f5f9", fontSize: 24, fontWeight: 700 }}>{value ?? "—"}</div>
    </div>
  );
}

// ── Node Card ─────────────────────────────────────────────
function NodeCard({ node }) {
  const cpuColor = node.cpu_percent > 70 ? "#ef4444" : node.cpu_percent > 40 ? "#f59e0b" : "#22c55e";
  const memColor = node.memory_percent > 70 ? "#ef4444" : node.memory_percent > 40 ? "#f59e0b" : "#22c55e";
  const isReady = node.status === "Ready";

  return (
    <div style={{ background: "#1e293b", borderRadius: 10, padding: 14, flex: 1, minWidth: 130 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <span style={{ color: "#f1f5f9", fontWeight: 600, fontSize: 12 }}>{node.name}</span>
        <span style={{
          background: isReady ? "#22c55e22" : "#ef444422",
          color: isReady ? "#22c55e" : "#ef4444",
          borderRadius: 6, padding: "2px 6px", fontSize: 9, fontWeight: 600
        }}>{node.status}</span>
      </div>
      <div style={{ color: "#64748b", fontSize: 9, marginBottom: 8 }}>
        {node.role} • {node.ip}
      </div>
      {[
        { label: "CPU", value: node.cpu_percent, color: cpuColor },
        { label: "RAM", value: node.memory_percent, color: memColor }
      ].map(({ label, value, color }) => (
        <div key={label} style={{ marginBottom: 5 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#94a3b8", marginBottom: 2 }}>
            <span>{label}</span>
            <span style={{ color }}>{value}%</span>
          </div>
          <div style={{ background: "#0f172a", borderRadius: 4, height: 4 }}>
            <div style={{ background: color, width: `${Math.min(value, 100)}%`, height: "100%", borderRadius: 4, transition: "width 1s ease" }} />
          </div>
        </div>
      ))}
      <div style={{ fontSize: 10, color: "#64748b", marginTop: 5 }}>
        🌡️ {node.temperature}°C  ⏱️ {node.uptime}
      </div>
    </div>
  );
}

// ── Live Camera Feed ──────────────────────────────────────
function CameraFeed({ liveFrame, latestDetection }) {
  const imageSrc = liveFrame
    ? `data:image/jpeg;base64,${liveFrame}`
    : latestDetection?.image_url || null;

  return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
      <h2 style={{ margin: "0 0 12px", fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>
        📷 Live Camera Feed
        {liveFrame && <span style={{ marginLeft: 8, background: "#ef444422", color: "#ef4444", borderRadius: 4, padding: "1px 6px", fontSize: 9 }}>● LIVE</span>}
      </h2>
      {imageSrc ? (
        <img
          src={imageSrc}
          alt="camera feed"
          style={{ width: "100%", borderRadius: 8, objectFit: "cover", maxHeight: 280 }}
        />
      ) : (
        <div style={{ height: 200, background: "#0f172a", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", color: "#64748b" }}>
          Waiting for camera...
        </div>
      )}
      {latestDetection && latestDetection.type && (
        <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
          <div style={{ background: "#0f172a", borderRadius: 8, padding: "6px 10px", flex: 1 }}>
            <div style={{ color: "#64748b", fontSize: 10 }}>Type</div>
            <div style={{ color: latestDetection.threat ? "#ef4444" : "#60a5fa", fontWeight: 600, fontSize: 13, textTransform: "capitalize" }}>
              {latestDetection.threat ? "⚠️ " : "✅ "}{latestDetection.type}
            </div>
          </div>
          <div style={{ background: "#0f172a", borderRadius: 8, padding: "6px 10px", flex: 1 }}>
            <div style={{ color: "#64748b", fontSize: 10 }}>Confidence</div>
            <div style={{ color: "#f1f5f9", fontWeight: 600, fontSize: 13 }}>
              {Math.round(latestDetection.confidence * 100)}%
            </div>
          </div>
          <div style={{ background: "#0f172a", borderRadius: 8, padding: "6px 10px", flex: 2 }}>
            <div style={{ color: "#64748b", fontSize: 10 }}>Classes</div>
            <div style={{ color: "#f1f5f9", fontSize: 11 }}>
              {latestDetection.classes?.join(", ")}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────
export default function App() {
  const stats = useApi("/api/stats", 5000);
  const clusterData = useApi("/api/cluster/nodes", 8000);
  const alertData = useApi("/api/alerts", 5000);
  const detectionsData = useApi("/api/detections", 3000);
  const latestDetection = useApi("/api/detections/latest", 2000);
  const { liveFrame, liveDetection } = useWebSocket();

  const currentDetection = liveDetection || latestDetection;

  return (
    <div style={{
      background: "#0f172a", minHeight: "100vh", color: "#f1f5f9",
      fontFamily: "Inter, system-ui, sans-serif", padding: "16px 20px"
    }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>🖥️ Edge Computing Monitor</h1>
          <div style={{ color: "#64748b", fontSize: 11 }}>Cloud Computing SS2026 — Frankfurt UAS — Group 8</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, background: "#1e293b", borderRadius: 8, padding: "6px 12px" }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e", display: "inline-block", animation: "pulse 2s infinite" }} />
          <span style={{ fontSize: 11 }}>Live</span>
        </div>
      </div>

      {/* Stats Bar */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <StatCard icon="👁️" label="Detections" value={stats?.total_detections_today} color="#60a5fa" />
        <StatCard icon="👤" label="People" value={stats?.total_people_detected} color="#a78bfa" />
        <StatCard icon="⚠️" label="Threats" value={stats?.total_threats_detected} color="#ef4444" />
        <StatCard icon="🎯" label="Accuracy" value={stats ? `${stats.detection_accuracy}%` : null} color="#22c55e" />
        <StatCard icon="🖥️" label="Nodes" value={stats ? `${stats.active_nodes}/${stats.total_nodes}` : null} color="#f59e0b" />
      </div>

      {/* Camera + Alerts */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 16, marginBottom: 16 }}>
        <CameraFeed liveFrame={liveFrame} latestDetection={currentDetection} />

        {/* Alerts */}
        <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
          <h2 style={{ margin: "0 0 12px", fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>🔔 Threat Alerts</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 300, overflowY: "auto" }}>
            {alertData?.alerts?.length > 0 ? alertData.alerts.map(a => (
              <div key={a.id} style={{
                background: "#0f172a", borderRadius: 8, padding: "10px 12px",
                borderLeft: `3px solid ${a.severity === "high" ? "#ef4444" : "#f59e0b"}`
              }}>
                <div style={{ color: "#f1f5f9", fontSize: 11 }}>{a.message}</div>
                <div style={{ color: "#64748b", fontSize: 9, marginTop: 3 }}>
                  {new Date(a.timestamp).toLocaleString()}
                </div>
              </div>
            )) : (
              <div style={{ color: "#64748b", fontSize: 12, textAlign: "center", marginTop: 20 }}>
                ✅ No active alerts
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Cluster Status */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <h2 style={{ margin: "0 0 12px", fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>🖧 Cluster Status</h2>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {clusterData?.nodes?.map(n => <NodeCard key={n.name} node={n} />) ||
            <div style={{ color: "#64748b" }}>Loading cluster data...</div>}
        </div>
      </div>

      {/* Recent Detections Table */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
        <h2 style={{ margin: "0 0 12px", fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>📋 Recent Detections</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
            <thead>
              <tr style={{ color: "#64748b", textAlign: "left", borderBottom: "1px solid #0f172a" }}>
                {["Time", "Type", "Classes", "Count", "Confidence", "Location", "Status"].map(h => (
                  <th key={h} style={{ padding: "6px 8px", fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {detectionsData?.detections?.map(d => (
                <tr key={d.id} style={{ borderTop: "1px solid #0f172a" }}>
                  <td style={{ padding: "6px 8px", color: "#94a3b8" }}>{new Date(d.timestamp).toLocaleTimeString()}</td>
                  <td style={{ padding: "6px 8px", textTransform: "capitalize", color: d.threat ? "#ef4444" : "#60a5fa" }}>{d.type}</td>
                  <td style={{ padding: "6px 8px", color: "#94a3b8" }}>{d.classes?.join(", ")}</td>
                  <td style={{ padding: "6px 8px" }}>{d.count}</td>
                  <td style={{ padding: "6px 8px" }}>{Math.round(d.confidence * 100)}%</td>
                  <td style={{ padding: "6px 8px", color: "#94a3b8" }}>{d.location}</td>
                  <td style={{ padding: "6px 8px" }}>
                    <span style={{
                      background: d.threat ? "#ef444422" : "#22c55e22",
                      color: d.threat ? "#ef4444" : "#22c55e",
                      borderRadius: 5, padding: "2px 6px", fontSize: 9, fontWeight: 600
                    }}>
                      {d.threat ? "⚠️ THREAT" : "✅ Safe"}
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
