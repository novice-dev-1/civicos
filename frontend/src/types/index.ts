export interface ResourceOut {
  id: string;
  type: "ambulance" | "hospital" | "police";
  name: string;
  lat: number;
  lng: number;
  capacity_total: number;
  capacity_used: number;
  specialty: string | null;
  equipment: string[] | null;
  jurisdiction: string | null;
  status: "AVAILABLE" | "BUSY" | "OFFLINE" | string;
}

export interface IncidentCreate {
  description: string;
  lat: number;
  lng: number;
}

export interface IncidentOut {
  id: string;
  description: string;
  type: string | null;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string | null;
  victims: number;
  specialty_required: string | null;
  lat: number | null;
  lng: number | null;
  status: string;
  priority_score: number | null;
  created_at: string;
  resolved_at: string | null;
  time_to_care_min: number | null;
}

export interface AssignmentOut {
  id: string;
  incident_id: string;
  resource_id: string;
  role: string | null;
  eta_min: number | null;
  distance_km: number | null;
  assigned_at: string;
}

export interface AuditLogOut {
  id: string;
  incident_id: string;
  agent_name: string | null;
  step: number | null;
  thought: string | null;
  action: string | null;
  alternatives: Record<string, unknown> | null;
  logged_at: string;
}

export interface IncidentDetail extends IncidentOut {
  assignments: AssignmentOut[];
  audit_logs: AuditLogOut[];
}

export interface KPIOut {
  avg_time_to_care?: number;
  avg_time_to_care_min?: number;
  resource_utilization: number;
  hospital_load_variance: number;
  incidents_resolved?: number;
}

export interface KPIComparisonOut {
  civicos: KPIOut;
  naive: KPIOut;
  improvement_pct: number;
}

export interface ForecastOut {
  shortage_predicted: boolean;
  shortage_in_min: number | null;
  recommendations: string[];
}

export interface AgentEvent {
  id: string;
  incident_id: string;
  agent: string;
  thought: string;
  action: string;
  alternatives: string[];
  timestamp: string;
}

export interface CounterfactualReq {
  incident_id: string;
  override: Record<string, string>;
}

export interface CounterfactualOut {
  original_plan: Record<string, unknown>;
  alternative_plan: Record<string, unknown>;
  time_to_care_delta: number;
  reasoning: string;
}
