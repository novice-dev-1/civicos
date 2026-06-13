from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.utils.broadcaster import subscribe, unsubscribe

router = APIRouter()


@router.get("/events")
async def events(request: Request, incident_id: str | None = None):
    q = subscribe(incident_id or "*")

    async def gen():
        try:
            yield {"event": "ping", "data": json.dumps({"ts": "ok"})}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield {
                        "event": msg["event"],
                        "data": json.dumps(msg["data"], default=str),
                    }
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": json.dumps({"ts": "keepalive"})}
        finally:
            unsubscribe(incident_id or "*", q)

    return EventSourceResponse(gen())
