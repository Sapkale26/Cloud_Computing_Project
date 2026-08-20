import { useState } from "react";
import { formatTime } from "../utils/format";
import { IconBell } from "./Icon";

export default function AlertsPanel({ alerts, loading }) {
  // The mock/API doesn't expose an acknowledge endpoint, so acknowledgements
  // are tracked locally — enough to demo the interaction without inventing
  // a fake write endpoint.
  const [acked, setAcked] = useState(() => new Set());

  const toggleAck = (id) => {
    setAcked((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const list = alerts?.alerts ?? [];

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">
          <IconBell /> Alert log
        </h2>
        {list.length > 0 && <span className="panel__count">{list.length}</span>}
      </div>

      {loading && list.length === 0 && <div className="panel__empty">Loading alerts…</div>}
      {!loading && list.length === 0 && <div className="panel__empty">No active alerts. All clear.</div>}

      <ul className="alert-log">
        {list.map((alert) => {
          const isAcked = acked.has(alert.id);
          return (
            <li
              key={alert.id}
              className={`alert-log__row alert-log__row--${alert.severity} ${
                isAcked ? "alert-log__row--acked" : ""
              }`}
            >
              <span className="alert-log__time">{formatTime(alert.timestamp)}</span>
              <span className="alert-log__message">{alert.message}</span>
              <button
                type="button"
                className="alert-log__ack"
                onClick={() => toggleAck(alert.id)}
                aria-pressed={isAcked}
              >
                {isAcked ? "Acked" : "Ack"}
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
