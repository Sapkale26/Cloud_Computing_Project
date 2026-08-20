// A small hand-drawn icon set so the project has no runtime icon
// dependency to install. Every icon shares the same 20x20 stroke style.
const base = {
  width: "1em",
  height: "1em",
  viewBox: "0 0 20 20",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export function IconActivity(props) {
  return (
    <svg {...base} {...props}>
      <path d="M2 10h3.5l2-6 4 12 2-8.5 1.5 2.5H18" />
    </svg>
  );
}

export function IconUsers(props) {
  return (
    <svg {...base} {...props}>
      <circle cx="7.5" cy="6.5" r="2.5" />
      <path d="M2.5 16c0-3 2.2-5 5-5s5 2 5 5" />
      <path d="M13 8a2.3 2.3 0 100-4.6" />
      <path d="M14 11.3c2.2.5 3.5 2.2 3.5 4.7" />
    </svg>
  );
}

export function IconAlertTriangle(props) {
  return (
    <svg {...base} {...props}>
      <path d="M10 3 1.8 17h16.4L10 3Z" />
      <path d="M10 8.3v3.7" />
      <circle cx="10" cy="14.3" r="0.15" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconShieldCheck(props) {
  return (
    <svg {...base} {...props}>
      <path d="M10 2.2 17 4.6v5.1c0 4.4-3 7-7 8.1-4-1.1-7-3.7-7-8.1V4.6L10 2.2Z" />
      <path d="M6.9 10.1l2.1 2.1 4-4.3" />
    </svg>
  );
}

export function IconServer(props) {
  return (
    <svg {...base} {...props}>
      <rect x="2.3" y="2.5" width="15.4" height="6" rx="1.2" />
      <rect x="2.3" y="11.5" width="15.4" height="6" rx="1.2" />
      <path d="M5.3 5.5h.01M5.3 14.5h.01" strokeWidth="2" />
    </svg>
  );
}

export function IconCpu(props) {
  return (
    <svg {...base} {...props}>
      <rect x="5" y="5" width="10" height="10" rx="1.4" />
      <rect x="8" y="8" width="4" height="4" />
      <path d="M7.5 2v2.2M12.5 2v2.2M7.5 15.8V18M12.5 15.8V18M2 7.5h2.2M2 12.5h2.2M15.8 7.5H18M15.8 12.5H18" />
    </svg>
  );
}

export function IconThermometer(props) {
  return (
    <svg {...base} {...props}>
      <path d="M9 3a1.5 1.5 0 013 0v7.6a3.5 3.5 0 11-3 0V3Z" />
      <path d="M9 9.5h3" />
    </svg>
  );
}

export function IconClock(props) {
  return (
    <svg {...base} {...props}>
      <circle cx="10" cy="10" r="7.3" />
      <path d="M10 6v4.2l3 1.8" />
    </svg>
  );
}

export function IconBell(props) {
  return (
    <svg {...base} {...props}>
      <path d="M5 8.2a5 5 0 0110 0c0 4 1.5 5.2 1.5 5.2h-13S5 12.2 5 8.2Z" />
      <path d="M8.2 15.8a1.9 1.9 0 003.6 0" />
    </svg>
  );
}

export function IconSearch(props) {
  return (
    <svg {...base} {...props}>
      <circle cx="8.7" cy="8.7" r="5.4" />
      <path d="M17 17l-4-4" />
    </svg>
  );
}

export function IconWifi(props) {
  return (
    <svg {...base} {...props}>
      <path d="M2.5 7.5a11 11 0 0115 0" />
      <path d="M5.3 10.6a7 7 0 019.4 0" />
      <path d="M8.1 13.7a3 3 0 013.8 0" />
      <circle cx="10" cy="16.4" r="0.15" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconWifiOff(props) {
  return (
    <svg {...base} {...props}>
      <path d="M2 2l16 16" />
      <path d="M5.3 10.6a7 7 0 019.4 0M2.5 7.5a11 11 0 013.4-2.4M14.1 5.1a11 11 0 013.4 2.4" />
      <path d="M8.1 13.7a3 3 0 013.8 0" />
      <circle cx="10" cy="16.4" r="0.15" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconMapPin(props) {
  return (
    <svg {...base} {...props}>
      <path d="M10 18s6-5.4 6-10a6 6 0 10-12 0c0 4.6 6 10 6 10Z" />
      <circle cx="10" cy="8" r="2.1" />
    </svg>
  );
}

export function IconLayers(props) {
  return (
    <svg {...base} {...props}>
      <path d="M10 2.5 2.5 7 10 11.5 17.5 7 10 2.5Z" />
      <path d="M2.5 10.5 10 15l7.5-4.5" />
      <path d="M2.5 14 10 18.5 17.5 14" />
    </svg>
  );
}

export function IconRefresh(props) {
  return (
    <svg {...base} {...props}>
      <path d="M16.5 10a6.5 6.5 0 10-1.9 4.6" />
      <path d="M16.5 5.5V10h-4.4" />
    </svg>
  );
}

export function IconGauge(props) {
  return (
    <svg {...base} {...props}>
      <path d="M3 13.5a7 7 0 1114 0" />
      <path d="M10 13.5 13 8" />
      <circle cx="10" cy="13.5" r="0.9" fill="currentColor" stroke="none" />
    </svg>
  );
}
