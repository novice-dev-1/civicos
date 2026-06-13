import pytest

from app.agents.graph import graph


@pytest.mark.asyncio
async def test_graph_runs_offline():
    state = {
        "incident_id": "test-1",
        "raw_description": "cardiac arrest near India Gate, 1 victim",
        "location": (28.6127, 77.2295),
        "minutes_waiting": 0.0,
    }
    out = await graph.ainvoke(state)
    assert "final_assignments" in out
    assert len(out.get("trace", [])) >= 5
    assert out.get("incident_type") in ("accident", "fire", "cardiac", "stroke", "other")
