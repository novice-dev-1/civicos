from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.ambulance import ambulance_agent
from app.agents.coordinator import coordinator_dispatch, coordinator_finalize
from app.agents.forecast import forecast_agent
from app.agents.hospital import hospital_agent
from app.agents.incident import incident_agent
from app.agents.police import police_agent
from app.agents.state import CivicState
from app.agents.traffic import traffic_agent


def build_graph():
    g = StateGraph(CivicState)
    g.add_node("incident", incident_agent)
    g.add_node("coord1", coordinator_dispatch)
    g.add_node("ambulance", ambulance_agent)
    g.add_node("hospital", hospital_agent)
    g.add_node("police", police_agent)
    g.add_node("traffic", traffic_agent)
    g.add_node("coord2", coordinator_finalize)
    g.add_node("forecast", forecast_agent)

    g.add_edge(START, "incident")
    g.add_edge("incident", "coord1")
    g.add_edge("coord1", "ambulance")
    g.add_edge("coord1", "hospital")
    g.add_edge("coord1", "police")
    g.add_edge("ambulance", "traffic")
    g.add_edge("ambulance", "coord2")
    g.add_edge("hospital", "coord2")
    g.add_edge("police", "coord2")
    g.add_edge("traffic", "coord2")
    g.add_edge("coord2", "forecast")
    g.add_edge("forecast", END)

    return g.compile()


graph = build_graph()
