from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.graph import graph
from app.db import async_session
from app.models import Assignment, Incident, Resource
from app.utils.distance import eta_minutes, km

router = APIRouter()


class CounterfactualBody(BaseModel):
    incident_id: str
    override: dict


@router.post("/counterfactual")
async def counterfactual(body: CounterfactualBody):
    async with async_session() as s:
        inc = (
            await s.execute(select(Incident).where(Incident.id == body.incident_id))
        ).scalar_one_or_none()
        if not inc:
            raise HTTPException(status_code=404, detail="incident not found")

        orig = (
            await s.execute(select(Assignment).where(Assignment.incident_id == inc.id))
        ).scalars().all()
        original_plan = [
            {
                "role": a.role,
                "resource_id": str(a.resource_id),
                "eta_min": a.eta_min,
                "distance_km": a.distance_km,
            }
            for a in orig
        ]
        original_eta = max((a.eta_min or 0) for a in orig) if orig else 0

        state = {
            "incident_id": str(inc.id),
            "raw_description": inc.description,
            "incident_type": inc.type or "other",
            "severity": inc.severity or "MEDIUM",
            "victims": inc.victims or 1,
            "specialty_required": inc.specialty_required or "general",
            "location": (inc.lat, inc.lng),
            "minutes_waiting": 0.0,
            "force_assignments": body.override,
            "trace": [],
        }
        out = await graph.ainvoke(state)
        alt_assignments = out.get("final_assignments", {})

        alt_plan = []
        max_eta = 0.0
        for role, rid in alt_assignments.items():
            if not rid:
                continue
            r = (
                await s.execute(select(Resource).where(Resource.id == rid))
            ).scalar_one_or_none()
            if not r:
                continue
            d = km(inc.lat, inc.lng, r.lat, r.lng)
            e = eta_minutes(d)
            max_eta = max(max_eta, e)
            alt_plan.append(
                {
                    "role": role,
                    "resource_id": str(rid),
                    "eta_min": e,
                    "distance_km": round(d, 2),
                }
            )

        delta = round((original_eta or max_eta) - max_eta, 1)
        trace = out.get("trace", [])
        return {
            "original_plan": original_plan,
            "alternative_plan": alt_plan,
            "time_to_care_delta_min": delta,
            "time_to_care_delta": delta,
            "reasoning": trace[-1]["thought"] if trace else "",
        }
