import type {
  CounterfactualOut,
  ForecastOut,
  IncidentCreate,
  IncidentDetail,
  KPIComparisonOut,
  KPIOut,
  ResourceOut,
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers,
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API ${response.status}: ${response.statusText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getResources(): Promise<ResourceOut[]> {
  return request<ResourceOut[]>("/resources");
}

export function getIncidents(): Promise<IncidentDetail[]> {
  return request<IncidentDetail[]>("/incidents");
}

export function getIncident(id: string): Promise<IncidentDetail> {
  return request<IncidentDetail>(`/incidents/${id}`);
}

export function createIncident(data: IncidentCreate): Promise<IncidentDetail> {
  return request<IncidentDetail>("/incidents", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function simulate(scenario: string): Promise<IncidentDetail> {
  return request<IncidentDetail>("/incidents/simulate", {
    method: "POST",
    body: JSON.stringify({ scenario }),
  });
}

export function getKPI(): Promise<KPIOut> {
  return request<KPIOut>("/kpi");
}

export const getKpiComparison = async (): Promise<KPIComparisonOut> => {
  const r = await fetch(`${API_BASE_URL}/kpi/comparison`);
  if (!r.ok) throw new Error(`kpi/comparison ${r.status}`);
  return r.json();
};

export const postCounterfactual = async (body: {
  incident_id: string;
  override: Record<string, string>;
}): Promise<CounterfactualOut> => {
  const r = await fetch(`${API_BASE_URL}/counterfactual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`counterfactual ${r.status}`);
  return r.json();
};

export const getForecast = async (): Promise<ForecastOut> => {
  const r = await fetch(`${API_BASE_URL}/forecast`);
  if (!r.ok) throw new Error(`forecast ${r.status}`);
  return r.json();
};

export function adminReset(): Promise<void> {
  return request<void>("/admin/reset?confirm=true", { method: "POST" });
}

export function getResourcesLoad(): Promise<
  { name: string; used: number; total: number; ratio: number }[]
> {
  return request("/resources/load");
}
