from __future__ import annotations

from sqlalchemy import select

from app.agents.trace_utils import trace_entry
from app.db import async_session
from app.models import Resource
from app.utils.broadcaster import publish_agent_step
from app.utils.distance import eta_minutes, km


def _score(distance_km: float, jurisdiction_match: bool) -> float:
    d_norm = max(0.0, 1.0 - (distance_km / 15.0))
    jur = 1.0 if jurisdiction_match else 0.5
    return round(100 * (0.5 * jur + 0.5 * d_norm), 1)


async def police_agent(state: dict) -> dict:
    lat, lng = state["location"]

    async with async_session() as s:
        rows = (
            await s.execute(
                select(Resource).where(
                    Resource.type == "police",
                    Resource.status == "AVAILABLE",
                )
            )
        ).scalars().all()

    candidates = []
    for r in rows:
        cap_free = max(0, (r.capacity_total or 1) - (r.capacity_used or 0))
        if cap_free <= 0:
            continue
        d = km(lat, lng, r.lat, r.lng)
        jurisdiction_match = r.jurisdiction is not None
        candidates.append(
            {
                "resource_id": str(r.id),
                "type": "police",
                "name": r.name,
                "distance_km": round(d, 2),
                "eta_min": eta_minutes(d),
                "score": _score(d, jurisdiction_match),
                "rejected": False,
                "rejection_reason": None,
            }
        )
    candidates.sort(key=lambda c: c["score"], reverse=True)
    candidates = candidates[:3]

    top = candidates[0]["name"] if candidates else "NONE"
    alts = [
        f"{c['name']} rejected: lower score ({c['score']})" for c in candidates[1:]
    ]
    step = trace_entry(
        "PoliceAgent",
        4,
        f"Scored {len(candidates)} police units; top is {top}",
        f"Selected {top}" if candidates else "No police available",
        alts,
    )
    await publish_agent_step(state, "PoliceAgent", step)
    return {"police_candidates": candidates, "trace": [step]}
