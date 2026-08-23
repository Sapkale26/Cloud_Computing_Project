# Task 8 — Frontend Dashboard

## Overview

The frontend is a single-page **React 18 + Vite** dashboard ("Edge Cluster Monitor") that gives a live, glanceable view of the whole edge-computing pipeline: the physical Pi cluster's health, the latest camera detection from the Hailo inference service, active threat alerts, and a searchable log of recent detections. It talks to the Node.js backend over plain REST/JSON and embeds a Grafana panel for deeper node metrics.

It is built as a static site (`vite build`), packaged into an `nginx:alpine` Docker image, and deployed as a Kubernetes Deployment on the k3s cluster running on Pi 5 + the Pi 3 workers, exposed via a NodePort on `192.168.50.1:30080`.

This document goes through every part of the frontend in the order a developer would actually build it — project setup, the data layer, then every UI component, then styling and deployment — and explains the reasoning ("why", not just "what") behind each decision, in the same spirit as the cluster/HPL/MPI task write-ups.

## Project Structure

```
services/frontend/
|-- index.html        single HTML entry point, loads /src/main.jsx as an ES module
|-- vite.config.js     Vite + @vitejs/plugin-react, no custom config needed
|-- package.json       2 runtime deps (react, react-dom), 2 dev deps (vite, plugin-react)
|-- .env.example       documents VITE_API_URL / VITE_GRAFANA_URL
|-- Dockerfile         nginx:alpine, copies the pre-built dist/ folder
|-- src/
|   |-- main.jsx       React root, StrictMode
|   |-- App.jsx        top-level layout, owns all 5 useApi() calls
|   |-- App.css        component-level styles
|   |-- index.css      design tokens (CSS custom properties) + global resets
|   |-- api/
|   |   `-- client.js  API_BASE constant, fetchJson() wrapper, ApiError class
|   |-- hooks/
|   |   |-- useApi.js    generic polling hook used by every panel
|   |   `-- useClock.js  1-second ticking clock for the header
|   |-- utils/
|   |   `-- format.js  formatTime / formatClock / formatPercent / statusTone
|   `-- components/
|       |-- Header.jsx
|       |-- ConnectionBanner.jsx
|       |-- TopologyStrip.jsx
|       |-- StatsGrid.jsx / StatCard.jsx
|       |-- LatestDetection.jsx  (contains the ConfidenceRing sub-component)
|       |-- AlertsPanel.jsx
|       |-- ClusterStatus.jsx / NodeCard.jsx  (NodeCard contains MetricBar)
|       |-- GrafanaPanel.jsx
|       |-- DetectionsTable.jsx
|       |-- Footer.jsx
|       `-- Icon.jsx  15 hand-drawn inline SVG icons, one file
```

Every concern lives in exactly one place: network access in `api/`, reusable stateful logic in `hooks/`, pure formatting helpers in `utils/`, and presentation in `components/`. Nothing outside `api/client.js` knows the API base URL, and nothing outside `hooks/useApi.js` knows how polling or retry logic works — every component just consumes the hook's return value.

## Component Tree

```
App
 |-- Header (brand, live clock, online/offline pill, API host)
 |-- ConnectionBanner (shown only when a poll call fails)
 |-- TopologyStrip (one colored chip per cluster node -- signature element)
 |-- StatsGrid
 |   `-- StatCard x 5 (detections today, people, threats, accuracy, active nodes)
 |-- main-grid
 |   |-- LatestDetection (image + confidence ring + metadata)
 |   `-- AlertsPanel (scrollable alert log, local acknowledge toggle)
 |-- ClusterStatus
 |   `-- NodeCard x N (per-node CPU/RAM bars, temperature, uptime)
 |-- GrafanaPanel (embedded iframe -> node_exporter dashboard)
 |-- DetectionsTable (search + filter tabs over the full detection log)
 `-- Footer
```

## Why These Technology Choices

### Why React + Vite (and not something else)?

| Alternative | Why it was not used |
|---|---|
| Plain HTML/JS/jQuery | Five independently-polling, independently-loading panels with shared status derivation (online/offline) is exactly the kind of state-driven UI React is good at; hand-rolled DOM updates would re-implement what hooks already give for free |
| Next.js / a meta-framework | There is no server-side rendering need and no routing — this is a single always-on kiosk view, so an SSR framework adds build complexity (and a Node.js runtime in the container) for no benefit |
| Vue / Svelte / Angular | React was the framework the team already knew from other coursework, which mattered more than any technical edge for a project this size |
| Create React App | CRA is effectively unmaintained; Vite's dev server starts and hot-reloads far faster, which matters when iterating on a Raspberry Pi over Wi-Fi |

Vite's production build is also what makes the deployment story simple: `vite build` outputs plain static files, so the runtime container is just nginx serving HTML/CSS/JS — no Node.js process needs to run on the cluster to serve the dashboard.

### Why no CSS framework (Tailwind, Bootstrap, MUI)?

- The whole UI uses one consistent dark "NOC monitor" palette — a handful of CSS custom properties in `index.css` gives every component the same colors/radii/fonts without a utility-class build step or a component library's opinions to work around.
- A utility-class framework (Tailwind) would need a PostCSS build step and a purge/JIT config; a component library (MUI) would ship its own theming system on top of ours. Neither pays for itself on an 11-component dashboard.
- Every custom property is one line to change (e.g. re-theme `--accent-cyan`) and it updates the whole app — the same leverage a design-token system gives, without a dependency.

### Why hand-drawn SVG icons instead of an icon library?

`Icon.jsx` defines 15 icons (wifi, wifi-off, alert-triangle, users, activity, shield-check, server, cpu, thermometer, clock, bell, search, map-pin, layers, refresh, gauge) as plain inline SVG functions sharing one base stroke style (20×20 viewBox, 1.6px stroke, round caps/joins, `currentColor` for fill/stroke). This avoids adding a package like `lucide-react` or `react-icons` purely to render about 15 shapes, keeps the icon color tied to CSS (color cascades into `currentColor` automatically — e.g. a status pill just sets its own text color and the icon follows), and means the bundle only ships exactly the icons actually used.

### Why a custom useApi hook instead of Redux / React Query / SWR?

- There is no client-side mutation, caching invalidation, or cross-component derived state complex enough to need Redux — every panel independently GETs its own endpoint on its own interval and renders it. A global store would add indirection without solving a problem the app actually has.
- React Query/SWR solve caching, dedup, and background refetch — genuinely useful, but for 5 endpoints on fixed 3-8s intervals, a ~30-line hook implements the one behavior that matters here (keep last-known-good data on error) directly, without learning a third-party cache API or adding it to the bundle.
- Every additional dependency is one more thing to keep updated on a student project with a hard demo deadline — the team optimized for "can be understood by reading one file" over "industry-standard library".

### Why polling instead of WebSockets / Server-Sent Events?

The backend already exposes plain REST endpoints (used by the Telegram bot and the mobile-friendly dashboard alike), so polling reuses the exact same API surface with zero extra backend work. A push channel (WebSocket/SSE) would need a persistent connection held open through the same NodePort/nginx path the static files are served from, plus reconnect logic on the frontend — meaningful extra complexity for data that changes at most every few seconds. Polling intervals (see below) are tuned per endpoint instead, which gets "close enough to real-time" for a dashboard without the operational cost of a stateful connection on constrained Pi hardware.

## Data Flow: the useApi Hook

Every panel is driven by a single reusable hook, `useApi(endpoint, intervalMs)`, instead of one bespoke fetch effect per component. It polls the given endpoint on a fixed interval and exposes `{ data, error, loading, lastUpdated, refresh }`.

```jsx
export function useApi(endpoint, intervalMs = 5000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  ...
  const load = useCallback(async () => {
    try {
      const json = await fetchJson(endpoint);
      if (!mountedRef.current) return;
      setData(json);     // only overwritten on SUCCESS
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err);     // data is left untouched on failure
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    load();
    const id = setInterval(load, intervalMs);
    return () => clearInterval(id);
  }, [load, intervalMs]);

  return { data, error, loading, lastUpdated, refresh: load };
}
```

**Why keep data untouched on a failed poll?** A dropped Wi-Fi hop or a Pi rebooting mid-demo is expected on this hardware. If a failed request cleared the state, every panel would flash empty every few seconds during any network hiccup. Instead the dashboard keeps showing the last-known-good values and raises a single, dashboard-wide `ConnectionBanner` so the person watching knows the data is stale without the UI going blank.

### Per-Panel Poll Intervals

`App.jsx` calls the hook five times with different intervals, matched to how fast each data source actually changes:

| Endpoint | Interval | Reasoning |
|---|---|---|
| `/api/detections/latest` | 3,000 ms | Camera feed is the most time-sensitive panel |
| `/api/stats` | 5,000 ms | Aggregate counters change slowly |
| `/api/alerts` | 5,000 ms | Alerts are infrequent but should feel prompt |
| `/api/detections` | 5,000 ms | Table view, not safety-critical to the second |
| `/api/cluster/nodes` | 8,000 ms | CPU/RAM/temp on a Pi 3 barely moves within 8s; reduces SSH-polling load on the backend |

### Why keep loading, error, and data as three separate states?

It would be simpler to collapse everything into one status enum, but the three booleans/values are genuinely independent and every panel needs a different combination of them: `loading` alone drives the very first skeleton render, `error` alone drives the dashboard-wide banner, and `data` alone drives what's on screen — including while `error` is simultaneously true, which is the whole point of the stale-data pattern. A single enum can't represent "have data AND currently erroring" without extra cases that just re-derive these three values anyway.

## Component Walkthrough

Every panel below follows the same contract: it receives its slice of API data plus a loading flag as props from `App.jsx`, and is otherwise a pure function of those props — no component calls `useApi` itself. Centralizing all five calls in `App.jsx` makes the full set of network dependencies visible in one place instead of scattered across the tree.

### Header

Shows the brand mark/title, a live clock (via `useClock`, ticking every second independently of any network poll), an online/offline status pill, and — on wider viewports only (`min-width: 900px`) — the raw API host it's currently pointed at. That last piece is deliberately hidden on narrow screens: it's a debugging aid for whoever is presenting the dashboard, not something a casual viewer needs, so it's the first thing dropped when space is tight.

`isOnline` is not its own API call — it's derived once in `App.jsx` as `!anyError`, where `anyError` is true if any of the five `useApi` calls currently has an error. This means "Live" only shows when every single data source is reachable, which is a deliberately conservative definition of "online" for a monitoring tool.

### ConnectionBanner

A single-line, dashboard-wide alert (`role="alert"`) that appears only when `anyError` is true, naming the exact `API_BASE` URL that couldn't be reached. One shared banner was chosen over five separate per-panel error messages so a total backend outage produces one clear signal instead of five redundant ones stacked down the page.

### TopologyStrip

The dashboard's signature element and the first thing rendered after the header — see below.

### StatsGrid / StatCard

Five identical `StatCard` instances (detections today, people detected, threats flagged, detection accuracy, active/total nodes), each just `{ label, value, icon, tone }`. Using one generic card component parameterized by `tone` (cyan/violet/red/green/amber, each mapped to a CSS custom property via `--tone-color`) instead of five bespoke components means the exact same layout/skeleton/hover logic is guaranteed consistent across all five, and adding a sixth stat later is a one-line addition to `StatsGrid.jsx`.

The value column shows a skeleton shimmer only while `loading && value === null` — once any value has ever loaded (including a stale one), the card keeps showing it rather than reverting to a skeleton on every subsequent poll, avoiding a distracting flicker every 5 seconds.

### LatestDetection + ConfidenceRing

Shows the most recent detection's image (served from MinIO), a threat/safe badge overlaid on the image, and a metadata grid (time, count, location, detected classes). A small inline `ConfidenceRing` sub-component renders the confidence percentage as a ring using a CSS `conic-gradient` rather than an SVG arc or a charting library — a conic-gradient needs zero extra markup or math beyond `percent * 3.6` (degrees per percentage point) and re-colors automatically between the cyan "safe" tone and red "threat" tone.

If the image fails to load (an expired MinIO URL, a network blip), an `onError` handler flips a local `imgFailed` flag and the image block is simply omitted — the metadata still renders underneath. This was chosen over a placeholder/broken-image icon because a blank image slot reads as "no photo available" whereas a broken-image icon reads as "something is wrong", which is misleading when only the photo, not the detection itself, failed to load.

### AlertsPanel

A scrollable list of active alerts, each with a timestamp, message, and severity-colored left border (amber for normal, red for high). Alerts can be marked "Acked" — but this state is tracked in a local `Set` (`useState(() => new Set())`) rather than sent to the backend, because the API does not currently expose a write endpoint for acknowledgement. The team's choice was to demo the interaction honestly with local-only state rather than build a fake write endpoint just to make the button "work" end-to-end — acknowledging is visual only and resets on page reload.

### ClusterStatus / NodeCard / MetricBar

Renders one `NodeCard` per cluster node with CPU% and memory% as horizontal `MetricBar`s, plus temperature and uptime in the footer. The control-plane node (Pi 5) gets a subtly different border color (`node-card--cp`) so it's visually distinguishable from the seven worker nodes at a glance, without needing a text label. Both CPU and memory bars share the same `statusTone()` thresholds as the topology chips, so a node that looks "red" in the strip at the top also shows red bars here — one consistent color vocabulary for health across the whole dashboard.

### GrafanaPanel

A plain `<iframe>` embedding the cluster's existing Grafana "Node Exporter Full" dashboard in kiosk mode, rather than re-implementing historical CPU/memory graphs in React. Grafana already does this well (it's already running on Pi 5, reading from Prometheus, which is already scraping node_exporter on every Pi) — embedding it avoids duplicating that whole pipeline just to draw a line chart the dashboard doesn't otherwise need.

### DetectionsTable

A searchable, filterable table of the full detection history (time, type, classes, count, confidence, location, status). Search and the three filter tabs (All/Threats/People) are wrapped in `useMemo`, re-computing the filtered list only when the raw rows, the filter, or the query text actually change — this matters because the underlying data re-polls every 5 seconds regardless of whether the user is typing, so without memoization every keystroke would re-filter against a list that just silently changed underneath it. Threat rows get a colored left-edge accent (`box-shadow: inset` rather than a border, so it doesn't shift the table's column widths) to make them scannable without reading the Status column.

### Footer

Static attribution text (team, course, hardware). The one component in the tree that takes no props and touches no API — included mainly so the dashboard doesn't end abruptly after the data table.

### Icon.jsx

All 15 icons share one base props object (viewBox, stroke width, line caps/joins) spread into each `<svg>`, so adding icon #16 is copy-pasting one function rather than reconciling a new shape against a design system. Every icon accepts and forwards arbitrary `...props`, so call sites can override size/class without the icon component needing to know about it.

## The Topology Strip

Rather than lead the dashboard with an abstract "big number" hero stat, the top of the page is a literal, compact read-out of the physical cluster: one chip per node (CP for control-plane, W for worker), colored green/amber/red from live CPU% and readiness. This is the actual thing being monitored — a Raspberry Pi cluster — made glanceable in under a second, and it doubles as a loading skeleton (8 shimmering placeholder chips) while the first `/api/cluster/nodes` response is in flight.

## Graceful Degradation Pattern

The same pattern repeats across every panel: render a skeleton while `loading && !data`, render the real content once data arrives, and render a small empty-state message ("Waiting for the first detection…", "No active alerts. All clear.") rather than nothing at all when a response is legitimately empty. This keeps layout stable and avoids the dashboard ever looking broken versus simply quiet.

## Backend API Surface Consumed

| Endpoint | Method | Used by | Purpose |
|---|---|---|---|
| `/api/stats` | GET | StatsGrid | Detections today, people, threats, accuracy, active/total nodes |
| `/api/detections/latest` | GET | LatestDetection | Most recent detection incl. MinIO image URL, confidence, class list |
| `/api/detections` | GET | DetectionsTable | Full detection log for the searchable/filterable table |
| `/api/alerts` | GET | AlertsPanel | Active threat alerts (severity, message, timestamp) |
| `/api/cluster/nodes` | GET | TopologyStrip, ClusterStatus | Per-node status/role/CPU%/RAM%/temp/uptime, via backend SSH to each Pi |

All five calls share one thin client (`api/client.js`): a single `API_BASE` constant and a `fetchJson()` wrapper that throws a typed `ApiError` on a non-2xx response, so every hook consumer handles failures the same way.

```js
// api/client.js — the entire network layer
export const API_BASE = import.meta.env.VITE_API_URL ||
  "http://localhost:5050";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function fetchJson(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    throw new ApiError(`${path} responded with ${res.status}`, res.status);
  }
  return res.json();
}
```

Why a custom `ApiError` class instead of just letting `fetch`'s own rejection propagate? Plain `fetch()` only rejects on a network-level failure (DNS, connection refused) — a 404 or 500 response is still a "successful" fetch as far as the Promise is concerned. Wrapping that check in `fetchJson()` means every caller gets the same failure signal (a thrown error) whether the Pi is unreachable or the backend returned a 500, so `useApi` only needs one catch block to cover both cases.

### Fields Each Panel Reads

Reverse-engineered from the components' own field access (e.g. `detection.confidence`, `node.cpu_percent`) rather than from a separate API spec:

| Endpoint | Key fields the frontend reads |
|---|---|
| `/api/stats` | `total_detections_today`, `total_people_detected`, `total_threats_detected`, `detection_accuracy`, `active_nodes`, `total_nodes` |
| `/api/detections/latest` | `type`, `threat` (bool), `confidence` (0-1), `timestamp`, `count`, `location`, `classes[]`, `image_url` |
| `/api/detections` | `detections[]` — each with the same shape as `/latest`, plus `id` |
| `/api/alerts` | `alerts[]` — each with `id`, `severity` (normal/high), `message`, `timestamp` |
| `/api/cluster/nodes` | `nodes[]` — each with `name`, `role` (control-plane/worker), `ip`, `status` (Ready/...), `cpu_percent`, `memory_percent`, `temperature`, `uptime` |

## Environment Configuration

The API base URL is injected at build time via Vite's `VITE_`-prefixed env vars, so the same build artifact can point at a local mock backend during development or the real Pi gateway in production without touching source:

```bash
# .env.example
# Local mock backend (server.js in the mock-backend folder):
VITE_API_URL=http://localhost:5050

# Real Pi cluster gateway, when deploying against hardware:
# VITE_API_URL=http://192.168.50.1:5000
```

The Grafana panel follows the same pattern with its own `VITE_GRAFANA_URL`, defaulting to the cluster's Node Exporter Full dashboard embedded in kiosk mode.

## Design System

All colors, spacing radii, and fonts are centralized as CSS custom properties in `index.css` — a dark "NOC monitor" theme rather than the browser default, deliberately chosen because a status dashboard that is meant to run on a screen continuously benefits from a low-glare, high-contrast palette where color is reserved for signal (green/amber/red status) rather than decoration.

| Token group | Examples | Purpose |
|---|---|---|
| Surfaces | `--bg`, `--bg-card`, `--bg-inset` | Layered dark backgrounds for depth without borders everywhere |
| Accent | `--accent-cyan`, `--accent-violet` | Brand color for icons, highlights, focus rings |
| Status | `--status-good/warn/bad` (+ `*-dim`) | Single source of truth for green/amber/red across every panel |
| Type | `--font-display`, `--font-body`, `--font-mono` | Space Grotesk for headings, Inter for body, JetBrains Mono for numeric/IP data |

Numeric and machine-readable values (IP addresses, timestamps, percentages, the API host in the header) consistently use `--font-mono` so they are visually distinct from prose labels — a small convention that makes the table and node cards much easier to scan.

### Status-Tone Thresholds

Every health color in the app — topology chips, CPU/memory bars, node badges — comes from one shared function in `utils/format.js`, so "what counts as a warning" is defined exactly once:

```js
export function statusTone(value, { warn = 40, bad = 70 } = {}) {
  if (value >= bad) return "bad";   // red — e.g. CPU >= 70%
  if (value >= warn) return "warn"; // amber — e.g. CPU >= 40%
  return "good";                    // green — below both thresholds
}
```

Defaults of 40%/70% were picked as reasonable general-purpose thresholds for CPU/memory on a Raspberry Pi 3 (1GB RAM, quad-core Cortex-A53) under light inference-adjacent load, not derived from a specific benchmark — they're intentionally exposed as an options argument so a future component could tighten them (e.g. memory on a 1GB Pi 3 arguably deserves a stricter "bad" threshold than CPU) without touching the shared function.

### Responsive Breakpoints

| Breakpoint | What changes |
|---|---|
| `max-width: 640px` | Dashboard outer padding and inter-section gap shrink, for phones |
| `max-width: 860px` | The two-column main-grid (Latest Detection + Alerts) collapses to a single column |
| `min-width: 900px` | The raw API host debug readout in the header becomes visible (hidden by default on narrow screens) |

The stat cards, topology chips, and node cards don't use fixed breakpoints at all — they use CSS Grid's `repeat(auto-fit/auto-fill, minmax(...))`, which reflows the column count continuously based on available width instead of jumping at a handful of hard-coded screen sizes. This was chosen because the dashboard genuinely needs to work at three very different widths in practice — a phone checking in remotely, a laptop during development, and the kiosk/TV screen the project is meant to run on — and auto-fit avoids hand-tuning a breakpoint for each.

## Accessibility & Resilience Details

- Every icon-only status pill/panel title carries an `aria-label` or is paired with visible text — nothing is color-only.
- `@media (prefers-reduced-motion: reduce)` collapses all shimmer/pulse animations to near-zero duration for users who've opted out of motion.
- The confidence ring, connection banner, and filter tabs all set `role`/`aria-*` attributes (`role="img"`, `role="alert"`, `role="tablist"`) so the dashboard is usable with a screen reader.
- Broken detection images (a MinIO object that expired or a network blip) fall back silently via `onError` instead of showing a broken-image icon.

## Build & Deployment

The frontend is built as static assets and served by nginx inside the cluster, matching how the rest of the stack runs on k3s.

```dockerfile
# Dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
```

```bash
# Rebuild and redeploy (run on Pi 5)
cd ~/app/frontend
npm run build
sudo docker build -t frontend:latest .
sudo docker save frontend:latest | sudo k3s ctr images import -
sudo kubectl rollout restart deployment/frontend
```

The image intentionally contains no Node.js runtime — `npm run build` happens once at build time on Pi 5, and the shipped container is just static files behind nginx. This keeps the pod lightweight enough to be comfortable on the resource-constrained k3s workers.

| Service | Where it runs | Exposure |
|---|---|---|
| Frontend | k3s Deployment (containerized) | NodePort `:30080` |
| Backend | Directly on Pi 5 (outside k3s) | Port `:5000` — needs SSH keys to reach Pi 3 nodes for live metrics |

**Why is the backend not also in Kubernetes?** It SSHs into every Pi 3 node on demand to collect CPU/RAM/temperature/uptime for the dashboard, and mounting SSH keys into a container added complexity without benefit at this scale — so it runs directly on Pi 5 with full filesystem access, while the frontend (which only needs outbound HTTP to the backend) is cleanly containerized.

## Known Limitations

In the same spirit as documenting the PXE-boot failure in Task 1, these are the frontend's known gaps rather than things left silently unfinished:

- **Alert acknowledgement is not persisted.** Because `/api/alerts` has no write endpoint yet, "Ack" state lives in a local React `Set` and resets on page reload or for anyone else viewing the same dashboard from a different browser.
- **No authentication.** The dashboard and the API it talks to are both reachable by anyone on the cluster's private LAN (`192.168.50.0/24`); this was an accepted trade-off given the network is already isolated behind Pi 5's NAT gateway.
- **Polling, not push.** At worst, a new detection or alert can take up to one full interval (3-8s depending on the panel) to appear, rather than being instant.
- **No offline/local persistence.** If the backend is unreachable for longer than the browser tab stays open, the dashboard has no cached history to fall back to beyond whatever was already in memory from the last successful poll.
- **Single language, no i18n.** All copy is hard-coded English text in the JSX rather than routed through a translation layer — acceptable for a course project with one audience.

## Key Takeaways

- **No framework bloat.** Plain CSS custom properties and hand-drawn SVG icons instead of Tailwind/MUI/an icon library keep the bundle small and dependency-free — appropriate for a dashboard that itself runs on constrained hardware.
- **One data-fetching pattern, five endpoints.** A single `useApi` hook with per-panel poll intervals replaces five bespoke fetch effects and keeps failure handling consistent everywhere.
- **Stale-but-visible beats blank.** Failed polls never clear existing data — only a banner signals the problem — which matters on hardware where Wi-Fi/SSH hiccups are routine.
- **The topology strip is the thesis of the UI.** Leading with a literal per-node health readout, instead of an abstract KPI, keeps the dashboard honest about what it's actually monitoring: nine physical Raspberry Pis.
- **Deployment mirrors the constraints of the cluster.** Frontend containerized on k3s; backend runs bare-metal on Pi 5 because it needs direct SSH access — a pragmatic split documented rather than hidden.

---
*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
