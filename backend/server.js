require("dotenv").config();

const express = require("express");
const pool = require("./db");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: "10mb" }));

const fallbackNodes = {
  nodes: [
    {
      name: "raspberrypi",
      role: "control-plane",
      status: "Ready",
      cpu_percent: 45.2,
      memory_percent: 62.1,
      temperature: 52.3,
      uptime: "10 hours, 30 minutes"
    },
    {
      name: "pi3-1",
      role: "worker",
      status: "Ready",
      cpu_percent: 12.5,
      memory_percent: 35.0,
      temperature: 48.1,
      uptime: "10 hours, 30 minutes"
    }
  ]
};

const fallbackLatestDetection = {
  id: 42,
  timestamp: "2026-06-16T14:30:00.000Z",
  type: "person",
  threat: false,
  confidence: 0.95,
  count: 3,
  location: "Zone A",
  classes: ["person", "smoke"],
  image_url: "http://192.168.50.1:9000/detections/detection_42.jpg"
};

const fallbackStats = {
  total_detections_today: 142,
  total_people_detected: 139,
  total_threats_detected: 3,
  detection_accuracy: 94.5,
  active_nodes: 6,
  total_nodes: 7
};

const fallbackDevices = [
  { deviceId: "raspberry_master1", status: "online", role: "master" },
  { deviceId: "raspberry_master2", status: "online", role: "master" },
  { deviceId: "raspberry_1", status: "pending", role: "camera" },
  { deviceId: "raspberry_2", status: "pending", role: "sensor" },
  { deviceId: "raspberry_3", status: "pending", role: "worker" },
  { deviceId: "raspberry_4", status: "pending", role: "worker" },
  { deviceId: "raspberry_5", status: "pending", role: "worker" },
  { deviceId: "raspberry_6", status: "pending", role: "worker" },
  { deviceId: "raspberry_7", status: "pending", role: "worker" }
];

app.get("/", (req, res) => {
  res.send("Backend connected to PostgreSQL");
});

app.post("/events", async (req, res) => {
  try {
    const { event_type, location, image_url } = req.body;

    const result = await pool.query(
      "INSERT INTO events (event_type, location, image_url) VALUES ($1, $2, $3) RETURNING *",
      [event_type, location, image_url]
    );

    res.json({
      message: "Event added successfully",
      event: result.rows[0]
    });
  } catch (error) {
    console.error("POST /events error:", error);
    res.status(500).json({ error: "Database error" });
  }
});

app.get("/events", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM events ORDER BY created_at DESC");
    res.json(result.rows);
  } catch (error) {
    console.error("GET /events error:", error);
    res.status(500).json({ error: "Database error" });
  }
});

app.get("/api/cluster/nodes", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT name, role, status, cpu_percent, memory_percent, temperature, uptime FROM cluster_nodes ORDER BY updated_at DESC"
    );

    if (result.rows.length > 0) {
      return res.json({ nodes: result.rows });
    }

    return res.json(fallbackNodes);
  } catch (error) {
    console.error("GET /api/cluster/nodes DB fallback:", error.message);
    return res.json(fallbackNodes);
  }
});

app.get("/api/devices", (req, res) => {
  res.json(fallbackDevices);
});

app.post("/api/detections", async (req, res) => {
  try {
    const {
      type,
      threat,
      confidence,
      count,
      location,
      classes,
      image_url
    } = req.body;

    const result = await pool.query(
      `INSERT INTO detections
       (type, threat, confidence, count, location, classes, image_url)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [
        type,
        threat ?? false,
        confidence,
        count,
        location,
        classes || [],
        image_url
      ]
    );

    res.json({
      success: true,
      detection: result.rows[0]
    });
  } catch (error) {
    console.error("POST /api/detections error:", error);
    res.status(500).json({ success: false, error: "Database error" });
  }
});

app.get("/api/detections", async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT
        id,
        created_at AS timestamp,
        type,
        threat,
        confidence,
        count,
        location,
        classes,
        image_url
       FROM detections
       ORDER BY created_at DESC
       LIMIT 50`
    );

    if (result.rows.length > 0) {
      return res.json({ detections: result.rows });
    }

    return res.json({ detections: [fallbackLatestDetection] });
  } catch (error) {
    console.error("GET /api/detections DB fallback:", error.message);
    return res.json({ detections: [fallbackLatestDetection] });
  }
});

app.get("/api/detections/latest", async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT
        id,
        created_at AS timestamp,
        type,
        threat,
        confidence,
        count,
        location,
        classes,
        image_url
       FROM detections
       ORDER BY created_at DESC
       LIMIT 1`
    );

    if (result.rows.length > 0) {
      return res.json(result.rows[0]);
    }

    return res.json(fallbackLatestDetection);
  } catch (error) {
    console.error("GET /api/detections/latest DB fallback:", error.message);
    return res.json(fallbackLatestDetection);
  }
});

app.get("/api/detection/latest", (req, res) => {
  res.redirect("/api/detections/latest");
});

app.get("/api/alerts", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT * FROM alerts ORDER BY created_at DESC"
    );

    return res.json({
      alerts: result.rows
    });
  } catch (error) {
    console.error("GET /api/alerts DB fallback:", error.message);

    return res.json({
      alerts: [
        {
          id: 41,
          timestamp: "2026-06-16T14:29:58.000Z",
          severity: "high",
          message: "Threat at Zone B (knife)",
          acknowledged: false,
          image_url: "http://192.168.50.1:9000/detections/detection_41.jpg"
        }
      ]
    });
  }
});

app.get("/api/stats", async (req, res) => {
  try {
    const detectionsToday = await pool.query(
      `SELECT COUNT(*)::int AS count
       FROM detections
       WHERE created_at::date = CURRENT_DATE`
    );

    const peopleDetected = await pool.query(
      `SELECT COALESCE(SUM(count), 0)::int AS count
       FROM detections
       WHERE type = 'person'
       AND created_at::date = CURRENT_DATE`
    );

    const threatsDetected = await pool.query(
      `SELECT COUNT(*)::int AS count
       FROM detections
       WHERE threat = true
       AND created_at::date = CURRENT_DATE`
    );

    const nodeStats = await pool.query(
      `SELECT
        COUNT(*)::int AS total_nodes,
        COUNT(*) FILTER (WHERE LOWER(status) IN ('ready', 'online'))::int AS active_nodes
       FROM cluster_nodes`
    );

    const dbStats = {
      total_detections_today: detectionsToday.rows[0].count,
      total_people_detected: peopleDetected.rows[0].count,
      total_threats_detected: threatsDetected.rows[0].count,
      detection_accuracy: 94.5,
      active_nodes: nodeStats.rows[0].active_nodes || 0,
      total_nodes: nodeStats.rows[0].total_nodes || 0
    };

    const hasRealData =
      dbStats.total_detections_today > 0 || dbStats.total_nodes > 0;

    if (hasRealData) {
      return res.json(dbStats);
    }

    return res.json(fallbackStats);
  } catch (error) {
    console.error("GET /api/stats DB fallback:", error.message);
    return res.json(fallbackStats);
  }
});

app.post("/api/preprocess", (req, res) => {
  const { image_base64 } = req.body;

  res.json({
    success: true,
    image_base64
  });
});

app.get("/api/health", (req, res) => {
  res.json({
    status: "healthy",
    service: "edge-monitoring-backend",
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`Server started on port ${PORT}`);
});