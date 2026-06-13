from __future__ import annotations

from app.agents.trace_utils import trace_entry
from app.utils.broadcaster import publish_agent_step


async def traffic_agent(state: dict) -> dict:
    candidates = state.get("ambulance_candidates", [])
    if not candidates:
        return {"corridor_plan": None, "trace": []}

    primary = candidates[0]
    eta = primary["eta_min"]
    sev = state.get("severity", "MEDIUM")
    needs_corridor = (sev in ("HIGH", "CRITICAL")) and eta > 6.0
    plan = None
    if needs_corridor:
        plan = {
            "eta_min": eta,
            "route_hint": "primary_arterial",
            "police_needed": 1,
            "rationale": f"ETA {eta} min exceeds 6-min threshold for {sev}",
        }

    step = trace_entry(
        "TrafficAgent",
        5,
        f"Primary ETA {eta} min, severity {sev}",
        "Generated corridor plan" if needs_corridor else "No corridor needed",
        [] if needs_corridor else ["Skipped corridor: ETA within threshold"],
    )
    await publish_agent_step(state, "TrafficAgent", step)
    return {"corridor_plan": plan, "trace": [step]}
