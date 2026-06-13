"""IncidentAgent — parses free-text into structured incident."""

from __future__ import annotations

from app.agents.trace_utils import trace_entry
from app.utils.broadcaster import publish_agent_step
from app.utils.llm import gemini_json
from app.utils.priority import priority_score

SYSTEM = """You parse emergency call transcripts into structured data.
Return ONLY valid JSON matching this schema:
{
  "type": "accident" | "fire" | "cardiac" | "stroke" | "other",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "victims": <int>,
  "specialty_required": "trauma" | "cardiac" | "burns" | "general" | "stroke",
  "special_notes": "<free text, e.g. 'pediatric', 'trapped under debris'>"
}
Rules:
- CRITICAL if: mass casualty, building collapse, severe burns, cardiac arrest, "unconscious", "not breathing"
- HIGH if: multiple injuries, "chest pain", "stroke symptoms"
- MEDIUM if: single injury, conscious
- LOW if: minor
- specialty: 'cardiac' for heart/STEMI; 'burns' for fire/thermal; 'trauma' for crash/accident/fall; 'stroke' for FAST symptoms; else 'general'
- victims: best estimate; default 1
"""


async def incident_agent(state: dict) -> dict:
    description = state.get("raw_description", "")
    minutes_waiting = float(state.get("minutes_waiting", 0.0))

    parsed = await gemini_json(description, system=SYSTEM)
    if not parsed or "type" not in parsed:
        text = description.lower()
        if any(k in text for k in ["fire", "burn", "smoke"]):
            parsed = {
                "type": "fire",
                "severity": "HIGH",
                "victims": 1,
                "specialty_required": "burns",
                "special_notes": "",
            }
        elif any(k in text for k in ["cardiac", "heart", "chest pain"]):
            parsed = {
                "type": "cardiac",
                "severity": "HIGH",
                "victims": 1,
                "specialty_required": "cardiac",
                "special_notes": "",
            }
        elif any(k in text for k in ["accident", "crash", "bus", "car"]):
            parsed = {
                "type": "accident",
                "severity": "MEDIUM",
                "victims": 1,
                "specialty_required": "trauma",
                "special_notes": "",
            }
        else:
            parsed = {
                "type": "other",
                "severity": "MEDIUM",
                "victims": 1,
                "specialty_required": "general",
                "special_notes": "",
            }

    pscore = priority_score(
        parsed["severity"],
        int(parsed["victims"]),
        minutes_waiting,
        parsed["specialty_required"],
    )

    step = trace_entry(
        "IncidentAgent",
        1,
        f"Parsed '{description[:60]}…' → {parsed}",
        (
            f"Set type={parsed['type']}, severity={parsed['severity']}, "
            f"victims={parsed['victims']}, specialty={parsed['specialty_required']}"
        ),
    )
    await publish_agent_step(state, "IncidentAgent", step)
    return {
        "incident_type": parsed["type"],
        "severity": parsed["severity"],
        "victims": int(parsed["victims"]),
        "specialty_required": parsed["specialty_required"],
        "special_notes": parsed.get("special_notes", ""),
        "priority_score": pscore,
        "trace": [step],
    }
