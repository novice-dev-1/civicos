"""Append-only trace helpers for LangGraph reducers."""

from __future__ import annotations

from datetime import datetime, timezone


def trace_entry(
    agent: str,
    step: int,
    thought: str,
    action: str,
    alternatives: list[str] | None = None,
) -> dict:
    return {
        "agent": agent,
        "step": step,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "thought": thought,
        "action": action,
        "alternatives": alternatives or [],
    }
