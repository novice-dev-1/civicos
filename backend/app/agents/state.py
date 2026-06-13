from __future__ import annotations

import operator
from datetime import datetime
from typing import Annotated, Any, Optional, TypedDict

from pydantic import BaseModel, Field


class ResourceCandidate(BaseModel):
    resource_id: str
    type: str
    name: str
    distance_km: float
    eta_min: float
    score: float = Field(ge=0, le=100)
    rejected: bool = False
    rejection_reason: Optional[str] = None


class AgentTrace(BaseModel):
    agent: str
    step: int
    timestamp: datetime
    thought: str
    action: str
    alternatives: list[str] = Field(default_factory=list)


class CivicState(TypedDict, total=False):
    incident_id: str
    raw_description: str
    incident_type: str
    severity: str
    victims: int
    specialty_required: str
    location: tuple[float, float]
    minutes_waiting: float
    priority_score: float
    ambulance_candidates: list[dict]
    hospital_candidates: list[dict]
    police_candidates: list[dict]
    corridor_plan: Optional[dict]
    final_assignments: dict
    trace: Annotated[list[dict], operator.add]
    forecast_warning: Optional[str]
    force_assignments: dict
    resource_shortage: bool
