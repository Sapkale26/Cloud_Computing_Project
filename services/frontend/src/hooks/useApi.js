import { useCallback, useEffect, useRef, useState } from "react";
import { fetchJson } from "../api/client";

/**
 * Polls an endpoint on an interval and keeps the last-known-good data
 * visible if a request fails, so the dashboard degrades gracefully
 * instead of blanking out on a dropped connection.
 */
export function useApi(endpoint, intervalMs = 5000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const mountedRef = useRef(true);

  const load = useCallback(async () => {
    try {
      const json = await fetchJson(endpoint);
      if (!mountedRef.current) return;
      setData(json);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    mountedRef.current = true;
    load();
    const id = setInterval(load, intervalMs);
    return () => {
      mountedRef.current = false;
      clearInterval(id);
    };
  }, [load, intervalMs]);

  return { data, error, loading, lastUpdated, refresh: load };
}
