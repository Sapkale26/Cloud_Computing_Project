const express = require("express");
const cors = require("cors");
const { NodeSSH } = require("node-ssh");
const app = express();

app.use(cors());
app.use(express.json());

// SSH credentials
const SSH_USER = "pi";
const SSH_PASS = "1234";

// Nodes config
const NODES = [
  { name: "raspberrypi", role: "control-plane", ip: "192.168.50.1" },
  { name: "pi3-1", role: "worker", ip: "192.168.50.91" },
  { name: "pi3-4", role: "worker", ip: "192.168.50.94" },
  { name: "pi3-5", role: "worker", ip: "192.168.50.95" },
  { name: "pi3-6", role: "worker", ip: "192.168.50.96" },
  { name: "pi3-7", role: "worker", ip: "192.168.50.97" },
];

async function getNodeStats(node) {
  const ssh = new NodeSSH();
  try {
    await ssh.connect({
      host: node.ip,
      username: SSH_USER,
      password: SSH_PASS,
      readyTimeout: 5000,
    });

    // Get CPU usage
    const cpuResult = await ssh.execCommand(
      "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'",
    );
    const cpu = parseFloat(cpuResult.stdout) || 0;

    // Get RAM usage
    const ramResult = await ssh.execCommand(
      "free | grep Mem | awk '{print $3/$2 * 100.0}'",
    );
    const ram = parseFloat(ramResult.stdout) || 0;

    // Get temperature
    const tempResult = await ssh.execCommand(
      "cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0",
    );
    const temp = parseFloat(tempResult.stdout) / 1000 || 0;

    // Get uptime
    const uptimeResult = await ssh.execCommand("uptime -p");
    const uptime = uptimeResult.stdout.replace("up ", "").trim();

    ssh.dispose();

    return {
      name: node.name,
      role: node.role,
      ip: node.ip,
      status: "Ready",
      cpu_percent: Math.round(cpu * 10) / 10,
      memory_percent: Math.round(ram * 10) / 10,
      temperature: Math.round(temp * 10) / 10,
      uptime,
    };
  } catch (err) {
    ssh.dispose();
    return {
      name: node.name,
      role: node.role,
      ip: node.ip,
      status: "Unreachable",
      cpu_percent: 0,
      memory_percent: 0,
      temperature: 0,
      uptime: "N/A",
    };
  }
}

// Mock data for detections (real data comes from object detection later)
const randomBetween = (min, max) =>
  Math.round((Math.random() * (max - min) + min) * 10) / 10;
const randomChoice = (arr) => arr[Math.floor(Math.random() * arr.length)];

const mockDetection = () => {
  const types = ["person", "person", "person", "threat"];
  const type = randomChoice(types);
  return {
    id: Math.floor(Math.random() * 1000),
    timestamp: new Date().toISOString(),
    type,
    confidence: randomBetween(0.75, 0.99),
    count: Math.floor(randomBetween(1, 5)),
    threat: type === "threat",
    location: randomChoice(["Zone A", "Zone B", "Zone C", "Entrance"]),
  };
};

// Routes
app.get("/api/cluster/nodes", async (req, res) => {
  try {
    const nodes = await Promise.all(NODES.map(getNodeStats));
    res.json({ nodes });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/detections", (req, res) => {
  res.json({ detections: Array.from({ length: 10 }, mockDetection) });
});

app.get("/api/detections/latest", (req, res) => {
  res.json(mockDetection());
});

app.get("/api/stats", (req, res) => {
  res.json({
    total_detections_today: Math.floor(randomBetween(100, 200)),
    total_people_detected: Math.floor(randomBetween(50, 150)),
    total_threats_detected: Math.floor(randomBetween(0, 10)),
    detection_accuracy: randomBetween(90, 99),
    active_nodes: 6,
    total_nodes: 7,
  });
});

app.get("/api/alerts", (req, res) => {
  res.json({
    alerts: [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        severity: "high",
        message: "Threat detected in Zone B",
        acknowledged: false,
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
        severity: "low",
        message: "Unknown person in Entrance",
        acknowledged: true,
      },
    ],
  });
});

app.listen(5000, () => console.log("Backend running on http://localhost:5000"));
