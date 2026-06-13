import { useIncidents } from "../hooks/useIncidents";
import { useCityStore } from "../store/cityStore";

export function Timeline() {
  const { data: incidents = [] } = useIncidents();
  const activeIncidentId = useCityStore((state) => state.activeIncidentId);
  const activeIncident =
    incidents.find((incident) => incident.id === activeIncidentId) ?? incidents[0];
  const auditLogs = activeIncident?.audit_logs ?? [];

  return (
    <section className="h-32 bg-[var(--color-panel)] px-4 py-3">
      <div className="flex h-full items-center gap-3 overflow-x-auto border border-dashed border-[var(--color-border)] px-4">
        {auditLogs.length === 0 ? (
          <p className="text-sm text-[var(--color-muted)]">Timeline is empty.</p>
        ) : (
          auditLogs.map((log) => (
            <div
              className="min-w-44 border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2"
              key={log.id}
            >
              <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">
                {log.agent_name}
              </p>
              <p className="mt-1 truncate text-sm text-[var(--color-text)]">
                {log.action}
              </p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
