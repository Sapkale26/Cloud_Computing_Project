export function formatTime(value) {
  if (!value) return "--:--:--";
  return new Date(value).toLocaleTimeString([], { hour12: false });
}

export function formatClock(date) {
  return date.toLocaleTimeString([], { hour12: false });
}

export function formatPercent(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${value.toFixed(digits)}%`;
}

export function statusTone(value, { warn = 40, bad = 70 } = {}) {
  if (value >= bad) return "bad";
  if (value >= warn) return "warn";
  return "good";
}
