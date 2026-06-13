from __future__ import annotations

from sqlalchemy import select

from app.agents.trace_utils import trace_entry
from app.db import async_session
from app.models import Resource
from app.utils.broadcaster import publish_agent_step
from app.utils.distance import eta_minutes, km


def _score(distance_km: float, equipment_match: bool, capacity_free: int) -> float:
    d_norm = max(0.0, 1.0 - (distance_km / 15.0))
    eq = 1.0 if equipment_match else 0.4
    cap = min(1.0, capacity_free / 3.0)
    return round(100 * (0.5 * d_norm + 0.3 * eq + 0.2 * cap), 1)


async def ambulance_agent(state: dict) -> dict:
    lat, lng = state["location"]
    specialty = state.get("specialty_required", "general")

    async with async_session() as s:
        rows = (
            await s.execute(
                select(Resource).where(
                    Resource.type == "ambulance",
                    Resource.status == "AVAILABLE",
                )
            )
        ).scalars().all()

    candidates = []
    for r in rows:
        d = km(lat, lng, r.lat, r.lng)
        equip = r.equipment or []
        equipment_match = (
            (specialty in equip) or ("ALS" in equip) or ("BLS" in equip)
        )
        cap_free = max(0, (r.capacity_total or 1) - (r.capacity_used or 0))
        candidates.append(
            {
                "resource_id": str(r.id),
                "type": "ambulance",
                "name": r.name,
                "distance_km": round(d, 2),
                "eta_min": eta_minutes(d),
                "score": _score(d, equipment_match, cap_free),
                "rejected": False,
                "rejection_reason": None,
            }
        )
    candidates.sort(key=lambda c: c["score"], reverse=True)
    candidates = candidates[:5]

    top = candidates[0]["name"] if candidates else "NONE"
    alts = [
        f"{c['name']} rejected: lower score ({c['score']})" for c in candidates[1:]
    ]
    step = trace_entry(
        "AmbulanceAgent",
        3,
        f"Scored {len(candidates)} available ambulances; top is {top}",
        f"Selected {top}" if candidates else "No ambulances available",
        alts,
    )
    await publish_agent_step(state, "AmbulanceAgent", step)
    return {"ambulance_candidates": candidates, "trace": [step]}
