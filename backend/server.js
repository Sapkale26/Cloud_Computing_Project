require("dotenv").config();

const express = require("express");
const pool = require("./db");

const app = express();

app.use(express.json());

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
      event: result.rows[0],
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Database error" });
  }
});

app.get("/events", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM events ORDER BY created_at DESC");
    res.json(result.rows);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Database error" });
  }
});

app.get("/api/cluster/nodes", (req, res) => {
  res.json({
    nodes: [
      {
        name: "raspberrypi",
        role: "control-plane",
        status: "Ready",
        cpu: 45.2,
        cpu_percent: 45.2,
        memory: 62.1,
        memory_percent: 62.1,
        temperature: 52.3,
        uptime: "10 hours, 30 minutes",
      },
     {
  name: "pi3-1",
  role: "worker",
  status: "Ready",
  cpu: 12.5,
  cpu_percent: 12.5,
  memory: 35.0,
  memory_percent: 35.0,
  temperature: 48.1,
  uptime: "10 hours, 30 minutes",
}
    ],
  });
});

app.get("/api/detection/latest", (req, res) => {
  res.redirect("/api/detections/latest");
});

app.get("/api/devices", (req, res) => {
  res.json([
    { deviceId: "raspberry_master1", status: "online", role: "master" },
    { deviceId: "raspberry_master2", status: "online", role: "master" },
    { deviceId: "raspberry_1", status: "pending", role: "camera" },
    { deviceId: "raspberry_2", status: "pending", role: "sensor" },
    { deviceId: "raspberry_3", status: "pending", role: "worker" },
    { deviceId: "raspberry_4", status: "pending", role: "worker" },
    { deviceId: "raspberry_5", status: "pending", role: "worker" },
    { deviceId: "raspberry_6", status: "pending", role: "worker" },
    { deviceId: "raspberry_7", status: "pending", role: "worker" }
  ]);
});

app.get("/api/alerts", (req, res) => {
  res.json({
    alerts: [
      {
        id: 41,
        timestamp: "2026-06-16T14:29:58.000Z",
        severity: "high",
        message: "Threat at Zone B (knife)",
        acknowledged: false,
        image_url: "http://192.168.50.1:9000/detections/detection_41.jpg",
      },
    ],
  });
});

app.get("/api/stats", (req, res) => {
  res.json({
    total_detections_today: 142,
    total_people_detected: 139,
    total_threats_detected: 3,
    detection_accuracy: 94.5,
    active_nodes: 6,
    total_nodes: 7,
  });
});


app.get("/api/detection/latest", (req, res) => {
  res.json({
    id: 42,
    timestamp: "2026-06-16T14:30:00.000Z",
    type: "person",
    threat: false,
    confidence: 0.95,
    count: 3,
    location: "Zone A",
    classes: ["person", "smoke"],
    image_url: "http://192.168.50.1:9000/detections/detection_42.jpg",
  });
});

app.get("/api/devices", (req, res) => {
  res.json([
    {
      deviceId: "raspberry_master1",
      status: "online",
      role: "master",
    },
    {
      deviceId: "raspberry_master2",
      status: "online",
      role: "master",
    },
    {
      deviceId: "raspberry_1",
      status: "pending",
      role: "camera",
    },
    {
      deviceId: "raspberry_2",
      status: "pending",
      role: "sensor",
    },
    {
      deviceId: "raspberry_3",
      status: "pending",
      role: "worker",
    },
    {
      deviceId: "raspberry_4",
      status: "pending",
      role: "worker",
    },
    {
      deviceId: "raspberry_5",
      status: "pending",
      role: "worker",
    },
    {
      deviceId: "raspberry_6",
      status: "pending",
      role: "worker",
    },
    {
      deviceId: "raspberry_7",
      status: "pending",
      role: "worker",
    },
  ]);
});


app.listen(3000, () => {
  console.log("Server started on port 3000");
});
