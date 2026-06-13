"""In-process pub/sub queue. One queue per incident_id.

   Phase 5 will add the SSE endpoint that subscribes here."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

_queues: dict[str, list[asyncio.Queue]] = defaultdict(list)


def subscribe(incident_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=200)
    _queues[incident_id].append(q)
    return q


def unsubscribe(incident_id: str, q: asyncio.Queue) -> None:
    if q in _queues.get(incident_id, []):
        _queues[incident_id].remove(q)


async def publish(incident_id: str, event: str, data: dict[str, Any]) -> None:
    payload = {"event": event, "data": data}
    for q in list(_queues.get(incident_id, [])):
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass
    for q in list(_queues.get("*", [])):
        if incident_id == "*":
            continue
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass


async def publish_agent_step(state: dict, agent: str, step: dict | None = None) -> None:
    try:
        entry = step
        if entry is None:
            trace = state.get("trace", [])
            if not trace:
                return
            entry = trace[-1]
        await publish(
            state.get("incident_id", ""),
            "agent_thought",
            {
                "incident_id": state.get("incident_id"),
                "agent": agent,
                "thought": entry["thought"],
                "action": entry["action"],
                "alternatives": entry.get("alternatives", []),
            },
        )
    except Exception:
        pass
