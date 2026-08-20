// Central place for talking to the detection backend.
//
// The base URL is configurable via VITE_API_URL so the same build can point
// at the local mock server during development or the real Pi cluster
// gateway in production, without touching code. See .env.example.
export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5050";

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
