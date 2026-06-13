import { Radio } from "lucide-react";
import { useState } from "react";

import { useIncidents } from "../hooks/useIncidents";
import { useCityStore } from "../store/cityStore";

const AGENT_COLORS: Record<string, string> = {
  IncidentAgent: "border-blue-400/50 bg-blue-500/10",
  CoordinatorAgent: "border-purple-400/50 bg-purple-500/10",
  AmbulanceAgent: "border-red-400/50 bg-red-500/10",
  HospitalAgent: "border-teal-400/50 bg-teal-500/10",
  PoliceAgent: "border-indigo-400/50 bg-indigo-500/10",
  TrafficAgent: "border-amber-400/50 bg-amber-500/10",
  ForecastAgent: "border-orange-400/50 bg-orange-500/10",
};

export function AgentFeed() {
  useIncidents();
  const traces = useCityStore((state) => state.traces);
  const activeIncidentId = useCityStore((state) => state.activeIncidentId);
  const [paused, setPaused] = useState(false);

  const filtered = activeIncidentId
    ? traces.filter((t) => t.incident_id === activeIncidentId)
    : traces;

  return (
    <section className="flex min-h-full flex-col">
      <div className="border-b border-[var(--color-border)] p-4">
        <h2 className="text-base font-semibold">Agent Feed</h2>
        <p className="mt-1 text-sm text-[var(--color-muted)]">Live SSE stream</p>
      </div>

      {filtered.length === 0 ? (
        <div className="grid flex-1 place-items-center px-5 text-center">
          <div>
            <Radio
              className="mx-auto size-8 text-[var(--color-muted)]"
              aria-hidden="true"
            />
            <p className="mt-3 text-sm text-[var(--color-muted)]">
              Agent reasoning appears after dispatch.
            </p>
          </div>
        </div>
      ) : (
        <div
          className="space-y-3 overflow-y-auto p-4"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
          style={{ scrollBehavior: paused ? "auto" : "smooth" }}
        >
          {filtered.map((log) => (
            <article
              className={`border p-3 ${
                AGENT_COLORS[log.agent] ??
                "border-[var(--color-border)] bg-[var(--color-bg)]"
              }`}
              key={log.id}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-xs font-semibold text-[var(--color-accent)]">
                  {log.agent}
                </span>
                <span className="text-[11px] text-[var(--color-muted)]">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="mt-2 text-sm text-[var(--color-text)]">{log.thought}</p>
              <p className="mt-2 border-l border-[var(--color-accent)] pl-2 text-xs text-[var(--color-muted)]">
                {log.action}
              </p>
              {log.alternatives.length > 0 && (
                <p className="mt-2 text-[10px] text-[var(--color-muted)]">
                  {log.alternatives.join(" · ")}
                </p>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
