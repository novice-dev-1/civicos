import { useEffect, useRef, useState } from "react";

import { useCityStore } from "../store/cityStore";

export function useSSE() {
  const esRef = useRef<EventSource | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const base =
      import.meta.env.VITE_API_URL?.replace(/\/$/, "") ||
      `${window.location.protocol}//${window.location.hostname}:8000`;
    const es = new EventSource(`${base}/events`);
    esRef.current = es;

    es.addEventListener("open", () => setConnected(true));
    es.addEventListener("agent_thought", (e) => {
      const data = JSON.parse((e as MessageEvent).data);
      useCityStore.getState().appendTrace(data);
    });
    es.addEventListener("corridor_generated", (e) => {
      const data = JSON.parse((e as MessageEvent).data);
      useCityStore.getState().setCorridor(data);
    });
    es.addEventListener("forecast_alert", (e) => {
      const data = JSON.parse((e as MessageEvent).data);
      useCityStore.getState().setForecast(data);
    });
    es.onerror = () => {
      setConnected(false);
      console.warn("[sse] disconnected, will retry");
    };

    return () => es.close();
  }, []);

  return connected;
}
