from __future__ import annotations

from sqlalchemy import select

from app.agents.trace_utils import trace_entry
from app.db import async_session
from app.models import Resource
from app.utils.broadcaster import publish_agent_step
from app.utils.distance import eta_minutes, km


def _score(
    distance_km: float, specialty_match: bool, icu_free: int, capacity_total: int
) -> float:
    d_norm = max(0.0, 1.0 - (distance_km / 15.0))
    spec = 1.0 if specialty_match else 0.4
    cap = min(1.0, icu_free / max(capacity_total, 1))
    return round(100 * (0.3 * d_norm + 0.4 * spec + 0.3 * cap), 1)


async def hospital_agent(state: dict) -> dict:
    lat, lng = state["location"]
    specialty = state.get("specialty_required", "general")

    async with async_session() as s:
        rows = (
            await s.execute(
                select(Resource).where(
                    Resource.type == "hospital",
                    Resource.status != "OFFLINE",
                )
            )
        ).scalars().all()

    candidates = []
    for r in rows:
        if (r.capacity_used or 0) >= (r.capacity_total or 1):
            continue
        d = km(lat, lng, r.lat, r.lng)
        specialty_match = r.specialty == specialty or r.specialty == "general"
        icu_free = max(0, (r.capacity_total or 1) - (r.capacity_used or 0))
        candidates.append(
            {
                "resource_id": str(r.id),
                "type": "hospital",
                "name": r.name,
                "distance_km": round(d, 2),
                "eta_min": eta_minutes(d),
                "score": _score(d, specialty_match, icu_free, r.capacity_total or 1),
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
        "HospitalAgent",
        4,
        f"Scored {len(candidates)} hospitals; top is {top}",
        f"Selected {top}" if candidates else "No hospitals available",
        alts,
    )
    await publish_agent_step(state, "HospitalAgent", step)
    return {"hospital_candidates": candidates, "trace": [step]}
