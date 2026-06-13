from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import func, select

from app.agents.trace_utils import trace_entry
from app.db import async_session
from app.models import Incident, Resource
from app.utils.broadcaster import publish_agent_step


async def forecast_agent(state: dict) -> dict:
    async with async_session() as s:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
        active = (
            await s.execute(
                select(func.count(Incident.id)).where(
                    Incident.created_at >= cutoff,
                    Incident.status.in_(("PENDING", "ASSIGNED")),
                )
            )
        ).scalar() or 0
        avail = (
            await s.execute(
                select(func.count(Resource.id)).where(Resource.status == "AVAILABLE")
            )
        ).scalar() or 0

    warning = None
    if active > 0 and avail > 0 and active >= avail:
        warning = (
            f"Resource shortage risk: {active} active incidents vs {avail} available "
            f"resources in last 60 min. Consider pre-positioning standby units."
        )
    elif avail == 0:
        warning = "No available resources. All units busy."

    step = trace_entry(
        "ForecastAgent",
        7,
        f"{active} active, {avail} available in last 60 min",
        warning or "No shortage predicted",
    )
    await publish_agent_step(state, "ForecastAgent", step)
    return {"forecast_warning": warning, "trace": [step]}
