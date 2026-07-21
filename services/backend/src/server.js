const express = require('express');
const cors = require('cors');
const { NodeSSH } = require('node-ssh');
const fs = require('fs');
const { exec } = require('child_process');
const Minio = require('minio');
const WebSocket = require('ws');

const app = express();
app.use(cors());
app.use(express.json({ limit: '20mb' }));

// ── MinIO Client ─────────────────────────────────────────
const minioClient = new Minio.Client({
  endPoint: '192.168.50.1',
  port: 9000,
  useSSL: false,
  accessKey: 'admin',
  secretKey: 'admin123'
});

async function ensureBucket() {
  try {
    const exists = await minioClient.bucketExists('detections');
    if (!exists) {
      await minioClient.makeBucket('detections');
      await minioClient.setBucketPolicy('detections', JSON.stringify({
        Version: '2012-10-17',
        Statement: [{ Effect: 'Allow', Principal: { AWS: ['*'] }, Action: ['s3:GetObject'], Resource: ['arn:aws:s3:::detections/*'] }]
      }));
    }
  } catch (err) { console.error('MinIO bucket error:', err.message); }
}
ensureBucket();

// ── SSH User Map ──────────────────────────────────────────
const SSH_USER_MAP = {
  'raspberrypi': 'pi',
  'pi3-1': 'pi3-1', 'pi3-2': 'pi3-2', 'pi3-3': 'pi3-3',
  'pi3-4': 'pi3-4', 'pi3-5': 'pi3-5', 'pi3-6': 'pi3-6', 'pi3-7': 'pi3-7',
};

const NODES = [
  { name: 'raspberrypi', role: 'control-plane', ip: '192.168.50.1' },
  { name: 'pi3-1', role: 'worker', ip: '192.168.50.91' },
  { name: 'pi3-2', role: 'worker', ip: '192.168.50.92' },
  { name: 'pi3-3', role: 'worker', ip: '192.168.50.93' },
  { name: 'pi3-4', role: 'worker', ip: '192.168.50.94' },
  { name: 'pi3-5', role: 'worker', ip: '192.168.50.95' },
  { name: 'pi3-6', role: 'worker', ip: '192.168.50.96' },
  { name: 'pi3-7', role: 'worker', ip: '192.168.50.97' },
];

// ── State ─────────────────────────────────────────────────
let detections = [];
let detectionId = 1;
let latestFrame = null;
let frameTimestamp = 0;
let activeWorkers = NODES.filter(n => n.role === 'worker').map(n => ({
  ip: n.ip, name: n.name, user: n.name
}));

// ── WebSocket Server ──────────────────────────────────────
const wss = new WebSocket.Server({ port: 5001 });
wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  ws.on('close', () => console.log('WebSocket client disconnected'));
});

function broadcast(data) {
  const msg = JSON.stringify(data);
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) client.send(msg);
  });
}

// ── MinIO Helpers ─────────────────────────────────────────
async function saveImage(base64, id) {
  try {
    const filename = `detection_${id}.jpg`;
    const buffer = Buffer.from(base64, 'base64');
    await minioClient.putObject('detections', filename, buffer, buffer.length, { 'Content-Type': 'image/jpeg' });
    return `http://192.168.50.1:9000/detections/${filename}`;
  } catch (err) {
    console.error('MinIO save error:', err.message);
    return null;
  }
}

async function cleanupMinIO() {
  try {
    const objects = [];
    const stream = minioClient.listObjects('detections', '', true);
    stream.on('data', obj => objects.push(obj));
    stream.on('end', async () => {
      if (objects.length > 100) {
        objects.sort((a, b) => new Date(a.lastModified) - new Date(b.lastModified));
        const toDelete = objects.slice(0, objects.length - 100);
        for (const obj of toDelete) await minioClient.removeObject('detections', obj.name);
        console.log(`Cleaned up ${toDelete.length} old images`);
      }
    });
  } catch (err) { console.error('MinIO cleanup error:', err.message); }
}
setInterval(cleanupMinIO, 5 * 60 * 1000);

// ── Node Stats via SSH ────────────────────────────────────
async function getNodeStats(node) {
  const ssh = new NodeSSH();
  const username = SSH_USER_MAP[node.name] || 'pi';
  try {
    await ssh.connect({ host: node.ip, username, password: '1234', readyTimeout: 5000 });
    const [cpu, ram, temp, uptime] = await Promise.all([
      ssh.execCommand("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"),
      ssh.execCommand("free | grep Mem | awk '{print $3/$2 * 100.0}'"),
      ssh.execCommand("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0"),
      ssh.execCommand("uptime -p")
    ]);
    ssh.dispose();
    return {
      name: node.name, role: node.role, ip: node.ip, status: 'Ready',
      cpu_percent: Math.round(parseFloat(cpu.stdout) * 10) / 10 || 0,
      memory_percent: Math.round(parseFloat(ram.stdout) * 10) / 10 || 0,
      temperature: Math.round(parseFloat(temp.stdout) / 1000 * 10) / 10 || 0,
      uptime: uptime.stdout.replace('up ', '').trim() || 'N/A',
    };
  } catch (err) {
    ssh.dispose();
    return { name: node.name, role: node.role, ip: node.ip, status: 'Unreachable', cpu_percent: 0, memory_percent: 0, temperature: 0, uptime: 'N/A' };
  }
}

// ── API Routes ────────────────────────────────────────────

// POST /api/detections — receive detection from Pi 4/Hailo
app.post('/api/detections', async (req, res) => {
  const { type, threat, confidence, count, location, classes, image_base64 } = req.body;
  const id = detectionId++;
  let image_url = null;
  if (image_base64) image_url = await saveImage(image_base64, id);
  const detection = { id, timestamp: new Date().toISOString(), type, threat, confidence, count, location, classes: classes || [], image_url };
  detections.unshift(detection);
  if (detections.length > 100) detections.pop();
  console.log(`Detection: ${type} (${confidence}) at ${location}`);
  broadcast({ type: 'detection', data: detection });
  res.json({ success: true, id });
});

// GET /api/detections — last 10
app.get('/api/detections', (req, res) => res.json({ detections: detections.slice(0, 10) }));

// GET /api/detections/latest
app.get('/api/detections/latest', (req, res) => res.json(detections[0] || {}));

// GET /api/cluster/nodes
app.get('/api/cluster/nodes', async (req, res) => {
  const nodes = await Promise.all(NODES.map(getNodeStats));
  res.json({ nodes });
});

// GET /api/stats
app.get('/api/stats', (req, res) => res.json({
  total_detections_today: detections.length,
  total_people_detected: detections.filter(d => !d.threat).length,
  total_threats_detected: detections.filter(d => d.threat).length,
  detection_accuracy: 94.5,
  active_nodes: 7,
  total_nodes: 7,
}));

// GET /api/alerts
app.get('/api/alerts', (req, res) => {
  const alerts = detections.filter(d => d.threat).slice(0, 5).map(d => ({
    id: d.id, timestamp: d.timestamp, severity: 'high',
    message: `Threat at ${d.location} (${d.classes.join(', ')})`,
    acknowledged: false, image_url: d.image_url
  }));
  res.json({ alerts });
});

// POST /api/preprocess — distribute frame to Pi 3 workers
app.post('/api/preprocess', (req, res) => {
  const { image_base64 } = req.body;
  const ts = Date.now();
  const tmpIn = `/tmp/frame_in_${ts}.jpg`;
  const tmpOut = `/tmp/frame_out_${ts}.jpg`;
  fs.writeFileSync(tmpIn, Buffer.from(image_base64, 'base64'));
  const cmd = `python3 /home/pi/cluster/services/pi3-preprocessing/parallel_preprocess.py ${tmpIn} ${tmpOut}`;
  exec(cmd, { timeout: 60000 }, (err, stdout, stderr) => {
    console.log(stdout);
    if (err || !fs.existsSync(tmpOut)) {
      if (fs.existsSync(tmpIn)) fs.unlinkSync(tmpIn);
      return res.json({ success: false, image_base64 });
    }
    const processed = fs.readFileSync(tmpOut);
    if (fs.existsSync(tmpIn)) fs.unlinkSync(tmpIn);
    if (fs.existsSync(tmpOut)) fs.unlinkSync(tmpOut);
    res.json({ success: true, image_base64: processed.toString('base64') });
  });
});

// POST/GET /api/frame — latest frame from Pi 4
app.post('/api/frame', (req, res) => {
  const { image_base64 } = req.body;
  latestFrame = image_base64;
  frameTimestamp = Date.now();
  broadcast({ type: 'frame', frame: image_base64 });
  res.json({ success: true });
});

app.get('/api/frame', (req, res) => {
  if (!latestFrame) return res.json({ frame: null, ts: 0 });
  res.json({ frame: latestFrame, ts: frameTimestamp });
});

// GET /api/stream — MJPEG stream
app.get('/api/stream', (req, res) => {
  res.setHeader('Content-Type', 'multipart/x-mixed-replace; boundary=frame');
  res.setHeader('Cache-Control', 'no-cache');
  const interval = setInterval(() => {
    if (!latestFrame) return;
    const buf = Buffer.from(latestFrame, 'base64');
    res.write('--frame\r\n');
    res.write('Content-Type: image/jpeg\r\n\r\n');
    res.write(buf);
    res.write('\r\n');
  }, 100);
  req.on('close', () => clearInterval(interval));
});

// POST/GET /api/workers — auto-scaling
app.post('/api/workers', (req, res) => {
  const { workers } = req.body;
  activeWorkers = workers;
  console.log(`Workers updated: ${workers.map(w => w.name).join(', ')}`);
  res.json({ success: true, count: workers.length });
});

app.get('/api/workers', (req, res) => res.json({ workers: activeWorkers }));

// GET /health
app.get('/health', (req, res) => res.json({ status: 'ok', timestamp: new Date().toISOString() }));

// ── Start ─────────────────────────────────────────────────
app.listen(5000, '0.0.0.0', () => {
  console.log('╔════════════════════════════════════════╗');
  console.log('║  Group 8 Backend API  →  port 5000     ║');
  console.log('║  WebSocket            →  port 5001     ║');
  console.log('╚════════════════════════════════════════╝');
});
