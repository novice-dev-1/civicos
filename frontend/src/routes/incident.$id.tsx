import { Link, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";

import { getIncident } from "../lib/api";

export function IncidentDetailPage() {
  const params = useParams({ from: "/incident/$id" });
  const { data: incident, isLoading, isError } = useQuery({
    queryKey: ["incident", params.id],
    queryFn: () => getIncident(params.id),
  });

  if (isLoading) {
    return (
      <main className="grid min-h-screen place-items-center bg-[var(--color-bg)] px-6 text-[var(--color-text)]">
        <p className="text-sm text-[var(--color-muted)]">Loading incident...</p>
      </main>
    );
  }

  if (isError || !incident) {
    return (
      <main className="grid min-h-screen place-items-center bg-[var(--color-bg)] px-6 text-[var(--color-text)]">
        <p className="text-sm text-red-300">Incident not found.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[var(--color-bg)] px-6 py-5 text-[var(--color-text)]">
      <Link
        className="inline-flex h-9 items-center gap-2 border border-[var(--color-border)] px-3 text-sm transition hover:border-[var(--color-accent)]"
        to="/"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Dashboard
      </Link>

      <section className="mt-6 max-w-3xl border border-[var(--color-border)] bg-[var(--color-panel)] p-6">
        <p className="text-xs uppercase tracking-[0.18em] text-[var(--color-muted)]">
          Incident Detail
        </p>
        <h1 className="mt-3 text-2xl font-semibold">{incident.description}</h1>

        <dl className="mt-6 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[var(--color-muted)]">Type</dt>
            <dd>{incident.type ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Severity</dt>
            <dd>{incident.severity ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Victims</dt>
            <dd>{incident.victims}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Status</dt>
            <dd>{incident.status}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Location</dt>
            <dd>
              {incident.lat != null && incident.lng != null
                ? `${incident.lat.toFixed(4)}, ${incident.lng.toFixed(4)}`
                : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Created</dt>
            <dd>{new Date(incident.created_at).toLocaleString()}</dd>
          </div>
        </dl>

        <div className="mt-8">
          <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--color-muted)]">
            Assignments
          </h2>
          {incident.assignments.length === 0 ? (
            <p className="mt-2 text-sm text-[var(--color-muted)]">No assignments yet.</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {incident.assignments.map((assignment) => (
                <li
                  className="border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm"
                  key={assignment.id}
                >
                  <span className="font-medium">{assignment.role}</span>
                  {" · "}
                  ETA {assignment.eta_min ?? "—"} min
                  {assignment.distance_km != null &&
                    ` · ${assignment.distance_km} km`}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-8">
          <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--color-muted)]">
            Agent Trace
          </h2>
          {incident.audit_logs.length === 0 ? (
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              No agent trace yet — Phase 4 will populate this.
            </p>
          ) : (
            <ul className="mt-3 space-y-3">
              {incident.audit_logs.map((log) => (
                <li
                  className="border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm"
                  key={log.id}
                >
                  <p className="font-medium text-[var(--color-accent)]">
                    {log.agent_name} (step {log.step ?? "—"})
                  </p>
                  <p className="mt-1">{log.thought}</p>
                  <p className="mt-1 text-[var(--color-muted)]">{log.action}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </main>
  );
}
