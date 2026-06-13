import { create } from "zustand";

import type { AgentEvent, IncidentDetail, KPIOut } from "../types";

interface CityState {
  incidents: IncidentDetail[];
  activeIncidentId: string | null;
  agentEvents: AgentEvent[];
  traces: AgentEvent[];
  corridor: Record<string, unknown> | null;
  forecast: Record<string, unknown> | null;
  kpi: KPIOut | null;
  demoMode: boolean;
  setIncidents: (incidents: IncidentDetail[]) => void;
  addIncident: (incident: IncidentDetail) => void;
  updateIncident: (incident: IncidentDetail) => void;
  setActiveIncident: (incidentId: string | null) => void;
  addAgentEvent: (event: AgentEvent) => void;
  appendTrace: (t: AgentEvent) => void;
  clearAgentEvents: () => void;
  setCorridor: (c: Record<string, unknown>) => void;
  setForecast: (f: Record<string, unknown>) => void;
  setKPI: (kpi: KPIOut) => void;
  toggleDemoMode: () => void;
}

export const useCityStore = create<CityState>((set) => ({
  incidents: [],
  activeIncidentId: null,
  agentEvents: [],
  traces: [],
  corridor: null,
  forecast: null,
  kpi: null,
  demoMode: false,
  setIncidents: (incidents) => set({ incidents }),
  addIncident: (incident) =>
    set((state) => ({ incidents: [incident, ...state.incidents] })),
  updateIncident: (incident) =>
    set((state) => ({
      incidents: state.incidents.map((current) =>
        current.id === incident.id ? incident : current,
      ),
    })),
  setActiveIncident: (incidentId) => set({ activeIncidentId: incidentId }),
  addAgentEvent: (event) =>
    set((state) => ({
      agentEvents: [...state.agentEvents, event].slice(-200),
    })),
  appendTrace: (t) =>
    set((state) => ({
      traces: [
        {
          id: `${t.incident_id}-${t.agent}-${Date.now()}`,
          incident_id: t.incident_id,
          agent: t.agent,
          thought: t.thought,
          action: t.action,
          alternatives: t.alternatives ?? [],
          timestamp: new Date().toISOString(),
        },
        ...state.traces,
      ].slice(0, 200),
    })),
  clearAgentEvents: () => set({ agentEvents: [], traces: [] }),
  setCorridor: (c) => set({ corridor: c }),
  setForecast: (f) => set({ forecast: f }),
  setKPI: (kpi) => set({ kpi }),
  toggleDemoMode: () => set((state) => ({ demoMode: !state.demoMode })),
}));
