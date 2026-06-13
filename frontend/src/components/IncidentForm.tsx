import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Flame, HeartPulse, MapPin, Send, Siren } from "lucide-react";

import { createIncident } from "../lib/api";
import { useCityStore } from "../store/cityStore";
import type { IncidentCreate } from "../types";

const SCENARIOS = [
  {
    label: "Bus",
    icon: Siren,
    description: "School bus crash near AIIMS, 15 children injured",
    lat: 28.5672,
    lng: 77.21,
  },
  {
    label: "Cardiac",
    icon: HeartPulse,
    description: "Cardiac arrest near India Gate, 1 patient with chest pain",
    lat: 28.6127,
    lng: 77.2295,
  },
  {
    label: "Fire",
    icon: Flame,
    description: "Building fire at Connaught Place, 8 people injured by burns",
    lat: 28.6315,
    lng: 77.2167,
  },
];

export function IncidentForm() {
  const queryClient = useQueryClient();
  const addIncident = useCityStore((state) => state.addIncident);
  const setActiveIncident = useCityStore((state) => state.setActiveIncident);
  const [form, setForm] = useState<IncidentCreate>({
    description: SCENARIOS[0].description,
    lat: SCENARIOS[0].lat,
    lng: SCENARIOS[0].lng,
  });

  const mutation = useMutation({
    mutationFn: createIncident,
    onSuccess: async (incident) => {
      addIncident(incident);
      setActiveIncident(incident.id);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["incidents"] }),
        queryClient.invalidateQueries({ queryKey: ["resources"] }),
      ]);
    },
  });

  return (
    <form
      className="space-y-3 border-b border-[var(--color-border)] p-4"
      onSubmit={(event) => {
        event.preventDefault();
        mutation.mutate(form);
      }}
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-base font-semibold">Incidents</h1>
          <p className="mt-1 text-xs text-[var(--color-muted)]">
            Live dispatch test
          </p>
        </div>
        <span className="border border-[var(--color-border)] px-2 py-1 text-xs text-[var(--color-muted)]">
          Delhi
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {SCENARIOS.map((scenario) => {
          const Icon = scenario.icon;
          return (
            <button
              className="flex h-9 items-center justify-center gap-1 border border-[var(--color-border)] text-xs transition hover:border-[var(--color-accent)]"
              key={scenario.label}
              onClick={() => setForm(scenario)}
              type="button"
            >
              <Icon className="size-3.5" aria-hidden="true" />
              {scenario.label}
            </button>
          );
        })}
      </div>

      <label className="block">
        <span className="sr-only">Incident description</span>
        <textarea
          className="min-h-24 w-full resize-none border border-[var(--color-border)] bg-[var(--color-bg)] p-3 text-sm text-[var(--color-text)] outline-none transition placeholder:text-[var(--color-muted)] focus:border-[var(--color-accent)]"
          maxLength={2000}
          minLength={3}
          onChange={(event) =>
            setForm((current) => ({
              ...current,
              description: event.target.value,
            }))
          }
          required
          value={form.description}
        />
      </label>

      <div className="grid grid-cols-[1fr_1fr_auto] gap-2">
        <label className="relative block">
          <span className="sr-only">Latitude</span>
          <MapPin
            className="pointer-events-none absolute left-2 top-1/2 size-3.5 -translate-y-1/2 text-[var(--color-muted)]"
            aria-hidden="true"
          />
          <input
            className="h-9 w-full border border-[var(--color-border)] bg-[var(--color-bg)] pl-7 pr-2 text-xs text-[var(--color-text)] outline-none focus:border-[var(--color-accent)]"
            max={90}
            min={-90}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                lat: Number(event.target.value),
              }))
            }
            step="0.0001"
            type="number"
            value={form.lat}
          />
        </label>
        <label className="block">
          <span className="sr-only">Longitude</span>
          <input
            className="h-9 w-full border border-[var(--color-border)] bg-[var(--color-bg)] px-2 text-xs text-[var(--color-text)] outline-none focus:border-[var(--color-accent)]"
            max={180}
            min={-180}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                lng: Number(event.target.value),
              }))
            }
            step="0.0001"
            type="number"
            value={form.lng}
          />
        </label>
        <button
          className="flex h-9 w-10 items-center justify-center border border-[var(--color-accent)] bg-[var(--color-accent)] text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={mutation.isPending}
          type="submit"
          title="Dispatch"
        >
          <Send className="size-4" aria-hidden="true" />
        </button>
      </div>

      {mutation.isError && (
        <p className="border border-red-500/40 bg-red-950/40 px-3 py-2 text-xs text-red-100">
          Dispatch failed. Check backend logs.
        </p>
      )}
    </form>
  );
}
