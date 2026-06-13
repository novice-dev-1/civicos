import {
  AlertTriangle,
  Clock3,
  MapPinned,
  RotateCcw,
  SlidersHorizontal,
} from "lucide-react";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useIncidents } from "../hooks/useIncidents";
import { adminReset, getKpiComparison } from "../lib/api";
import { useCityStore } from "../store/cityStore";
import type { IncidentDetail } from "../types";
import { IncidentForm } from "./IncidentForm";

function severityClass(severity: string | null) {
  if (severity === "CRITICAL") {
    return "border-red-400/40 bg-red-500/15 text-red-100";
  }
  if (severity === "HIGH") {
    return "border-orange-400/40 bg-orange-500/15 text-orange-100";
  }
  if (severity === "MEDIUM") {
    return "border-yellow-400/40 bg-yellow-500/15 text-yellow-100";
  }
  return "border-slate-500/40 bg-slate-500/15 text-slate-100";
}

function ageLabel(createdAt: string) {
  const minutes = Math.max(
    0,
    Math.floor((Date.now() - new Date(createdAt).getTime()) / 60_000),
  );
  if (minutes < 1) {
    return "now";
  }
  return `${minutes}m`;
}

function IncidentRow({
  incident,
  active,
  onSelect,
}: {
  incident: IncidentDetail;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      className={`w-full border p-3 text-left transition ${
        active
          ? "border-[var(--color-accent)] bg-cyan-500/10"
          : "border-[var(--color-border)] bg-[var(--color-bg)] hover:border-[var(--color-accent)]"
      }`}
      onClick={onSelect}
      type="button"
    >
      <div className="flex items-center justify-between gap-2">
        <span
          className={`border px-2 py-0.5 text-[10px] font-semibold ${severityClass(
            incident.severity,
          )}`}
        >
          {incident.severity ?? "UNKNOWN"}
        </span>
        <span className="flex items-center gap-1 text-[11px] text-[var(--color-muted)]">
          <Clock3 className="size-3" aria-hidden="true" />
          {ageLabel(incident.created_at)}
        </span>
      </div>
      <p className="mt-2 line-clamp-2 text-sm text-[var(--color-text)]">
        {incident.description}
      </p>
      <div className="mt-3 flex items-center justify-between text-xs text-[var(--color-muted)]">
        <span>{incident.status}</span>
        <span>{incident.assignments.length} assigned</span>
      </div>
    </button>
  );
}

export function IncidentList() {
  const queryClient = useQueryClient();
  const { data: incidents = [], isLoading, isError } = useIncidents();
  const activeIncidentId = useCityStore((state) => state.activeIncidentId);
  const setActiveIncident = useCityStore((state) => state.setActiveIncident);
  const setIncidents = useCityStore((state) => state.setIncidents);
  const [compareMessage, setCompareMessage] = useState<string | null>(null);
  const resetMutation = useMutation({
    mutationFn: adminReset,
    onSuccess: async () => {
      setIncidents([]);
      setActiveIncident(null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["incidents"] }),
        queryClient.invalidateQueries({ queryKey: ["resources"] }),
      ]);
    },
  });

  return (
    <section className="flex min-h-full flex-col">
      <IncidentForm />

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {isLoading && (
          <p className="px-2 py-3 text-sm text-[var(--color-muted)]">
            Loading incidents...
          </p>
        )}

        {isError && (
          <div className="border border-red-500/40 bg-red-950/40 p-3 text-sm text-red-100">
            <AlertTriangle className="mb-2 size-4" aria-hidden="true" />
            Incident feed unavailable.
          </div>
        )}

        {!isLoading && !isError && incidents.length === 0 && (
          <div className="grid h-full place-items-center px-5 text-center">
            <div>
              <MapPinned
                className="mx-auto size-8 text-[var(--color-muted)]"
                aria-hidden="true"
              />
              <p className="mt-3 text-sm text-[var(--color-muted)]">
                No active incidents yet.
              </p>
            </div>
          </div>
        )}

        <div className="space-y-2">
          {incidents.map((incident) => (
            <IncidentRow
              active={incident.id === activeIncidentId}
              incident={incident}
              key={incident.id}
              onSelect={() => setActiveIncident(incident.id)}
            />
          ))}
        </div>
      </div>

      <div className="space-y-2 border-t border-[var(--color-border)] p-4">
        <button
          className="flex h-9 w-full items-center justify-center gap-2 border border-[var(--color-border)] text-sm text-[var(--color-text)] transition hover:border-[var(--color-accent)]"
          disabled={resetMutation.isPending}
          onClick={() => {
            if (!window.confirm("Are you sure? This clears all incidents.")) {
              return;
            }
            resetMutation.mutate();
          }}
          type="button"
        >
          <RotateCcw className="size-4" aria-hidden="true" />
          {resetMutation.isPending ? "Resetting" : "Reset City"}
        </button>
        <button
          className="flex h-9 w-full items-center justify-center gap-2 border border-[var(--color-border)] text-sm text-[var(--color-text)] transition hover:border-[var(--color-accent)]"
          onClick={async () => {
            try {
              await getKpiComparison();
              setCompareMessage(null);
            } catch {
              setCompareMessage("Comparison view coming in Phase 8");
            }
          }}
          type="button"
        >
          <SlidersHorizontal className="size-4" aria-hidden="true" />
          Compare
        </button>
        {compareMessage && (
          <p className="text-center text-xs text-[var(--color-muted)]">
            {compareMessage}
          </p>
        )}
      </div>
    </section>
  );
}
