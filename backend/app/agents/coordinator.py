"""CoordinatorAgent — picks final assignments from candidates."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.agents.trace_utils import trace_entry
from app.db import async_session
from app.models import Resource
from app.utils.broadcaster import publish_agent_step
from app.utils.llm import gemini_json

SYSTEM_FINAL = """You are the final emergency coordinator. Given ranked candidates for
ambulance, hospital, and police, pick exactly ONE per role.
Return ONLY valid JSON:
{
  "final_assignments": {
    "primary_ambulance": "<resource_id or null>",
    "hospital":          "<resource_id or null>",
    "police":            "<resource_id or null>"
  },
  "rejections": [
    {"resource_id": "...", "reason": "..."}
  ]
}
Reject with a reason for every candidate NOT picked. Be terse. Reasons ≤ 12 words."""


async def coordinator_finalize(state: dict) -> dict:
    amb = list(state.get("ambulance_candidates", []))
    hosp = list(state.get("hospital_candidates", []))
    pol = list(state.get("police_candidates", []))

    async with async_session() as s:
        busy = set(
            (await s.execute(select(Resource.id).where(Resource.status == "BUSY")))
            .scalars()
            .all()
        )

    for grp in (amb, hosp, pol):
        grp[:] = [c for c in grp if uuid.UUID(c["resource_id"]) not in busy]

    final = {
        "primary_ambulance": amb[0]["resource_id"] if amb else None,
        "hospital": hosp[0]["resource_id"] if hosp else None,
        "police": pol[0]["resource_id"] if pol else None,
    }
    rejections = []
    for grp in (amb, hosp, pol):
        for c in grp[1:]:
            rejections.append(
                {
                    "resource_id": c["resource_id"],
                    "reason": f"Lower score ({c['score']}) than top pick",
                }
            )

    forced = state.get("force_assignments")
    if forced:
        final = {**final, **{k: v for k, v in forced.items() if v}}
    else:
        prompt = f"""Severity={state.get('severity')}, specialty={state.get('specialty_required')},
victims={state.get('victims')}, location={state.get('location')}.
Ambulance: {amb[:3]}
Hospital: {hosp[:3]}
Police: {pol[:3]}
Pick final and write rejections for the rest."""
        llm_out = await gemini_json(prompt, system=SYSTEM_FINAL)
        if isinstance(llm_out, dict) and isinstance(
            llm_out.get("final_assignments"), dict
        ):
            final.update(
                {k: v for k, v in llm_out["final_assignments"].items() if v}
            )
            if isinstance(llm_out.get("rejections"), list):
                rejections = llm_out["rejections"]

    rejected_ids = {r["resource_id"] for r in rejections}
    for grp in (amb, hosp, pol):
        for c in grp:
            if c["resource_id"] in rejected_ids:
                c["rejected"] = True
                for r in rejections:
                    if r["resource_id"] == c["resource_id"]:
                        c["rejection_reason"] = r.get("reason", "")
                        break

    shortage = any(v is None for v in final.values())
    thought = f"Final picks: {final}"
    if shortage:
        thought = "Critical Resource Shortage — " + thought
    step = trace_entry(
        "CoordinatorAgent",
        6,
        thought,
        "Plan finalized" if not shortage else "Critical Resource Shortage",
        [r.get("reason", "") for r in rejections[:5]],
    )
    await publish_agent_step(state, "CoordinatorAgent", step)
    return {
        "final_assignments": final,
        "ambulance_candidates": amb,
        "hospital_candidates": hosp,
        "police_candidates": pol,
        "trace": [step],
        "resource_shortage": shortage,
    }


async def coordinator_dispatch(state: dict) -> dict:
    step = trace_entry(
        "CoordinatorAgent",
        2,
        (
            f"Triaging {state.get('severity')} {state.get('incident_type')}, "
            f"fanning out to specialists"
        ),
        "Dispatched to Ambulance/Hospital/Police/Traffic agents in parallel",
    )
    await publish_agent_step(state, "CoordinatorAgent", step)
    return {"trace": [step]}
