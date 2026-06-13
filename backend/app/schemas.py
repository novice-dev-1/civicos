from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResourceOut(BaseModel):
    id: uuid.UUID
    type: str
    name: str
    lat: float
    lng: float
    capacity_total: int
    capacity_used: int
    specialty: str | None = None
    equipment: list[str] | None = None
    jurisdiction: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class IncidentCreate(BaseModel):
    description: str = Field(min_length=3, max_length=2000)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class IncidentOut(BaseModel):
    id: uuid.UUID
    description: str
    type: str | None = None
    severity: str | None = None
    victims: int
    specialty_required: str | None = None
    lat: float | None = None
    lng: float | None = None
    status: str
    priority_score: float | None = None
    created_at: datetime
    resolved_at: datetime | None = None
    time_to_care_min: float | None = None

    model_config = ConfigDict(from_attributes=True)


class AssignmentOut(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    resource_id: uuid.UUID
    role: str | None = None
    eta_min: float | None = None
    distance_km: float | None = None
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogOut(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    agent_name: str | None = None
    step: int | None = None
    thought: str | None = None
    action: str | None = None
    alternatives: dict[str, Any] | None = None
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentDetail(IncidentOut):
    assignments: list[AssignmentOut]
    audit_logs: list[AuditLogOut]


class KPIOut(BaseModel):
    avg_time_to_care: float
    resource_utilization: float
    hospital_load_variance: float


class SimulateRequest(BaseModel):
    scenario: str = Field(min_length=1, max_length=100)


class CounterfactualReq(BaseModel):
    incident_id: uuid.UUID
    override: dict[str, str]


class CounterfactualOut(BaseModel):
    original_plan: dict[str, Any]
    alternative_plan: dict[str, Any]
    time_to_care_delta: float
    reasoning: str


class KPIComparisonOut(BaseModel):
    civicos: KPIOut
    naive: KPIOut
    improvement_pct: float


class ForecastOut(BaseModel):
    shortage_predicted: bool
    shortage_in_min: int | None = None
    recommendations: list[str]
