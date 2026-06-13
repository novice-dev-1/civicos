from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.graph import graph
from app.db import async_session, get_db
from app.models import Assignment, AuditLog, Incident, Resource
from app.routers.resources import invalidate_resource_cache
from app.schemas import IncidentCreate, IncidentDetail, SimulateRequest


router = APIRouter(tags=["incidents"])


async def fetch_incident_detail(db: AsyncSession, incident_id: str) -> Incident:
    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .options(selectinload(Incident.assignments), selectinload(Incident.audit_logs))
    )
    incident = result.scalar_one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


async def _persist_graph_result(
    db: AsyncSession,
    incident: Incident,
    result: dict,
) -> None:
    incident.type = result.get("incident_type", incident.type)
    incident.severity = result.get("severity", incident.severity)
    incident.victims = result.get("victims", incident.victims)
    incident.specialty_required = result.get(
        "specialty_required", incident.specialty_required
    )
    incident.priority_score = result.get("priority_score", 0.0)

    final = result.get("final_assignments", {})
    has_ambulance = final.get("primary_ambulance")
    if result.get("resource_shortage"):
        incident.status = "FAILED"
    elif has_ambulance:
        incident.status = "ASSIGNED"
    else:
        incident.status = "PENDING"

    role_map = {
        "primary_ambulance": "primary_ambulance",
        "hospital": "hospital",
        "police": "police",
    }
    all_candidates = (
        result.get("ambulance_candidates", [])
        + result.get("hospital_candidates", [])
        + result.get("police_candidates", [])
    )

    for role_key, role_label in role_map.items():
        rid = final.get(role_key)
        if not rid:
            continue
        c = next((c for c in all_candidates if c["resource_id"] == rid), None)
        db.add(
            Assignment(
                incident_id=incident.id,
                resource_id=uuid.UUID(rid),
                role=role_label,
                eta_min=c["eta_min"] if c else None,
                distance_km=c["distance_km"] if c else None,
            )
        )
        res = (
            await db.execute(select(Resource).where(Resource.id == uuid.UUID(rid)))
        ).scalar_one()
        res.capacity_used = min(res.capacity_total, (res.capacity_used or 0) + 1)
        if res.capacity_used >= res.capacity_total:
            res.status = "BUSY"

    for step in result.get("trace", []):
        alts = step.get("alternatives", [])
        db.add(
            AuditLog(
                incident_id=incident.id,
                agent_name=step["agent"],
                step=step["step"],
                thought=step["thought"],
                action=step["action"],
                alternatives={"items": alts} if isinstance(alts, list) else alts,
            )
        )

    if result.get("resource_shortage"):
        db.add(
            AuditLog(
                incident_id=incident.id,
                agent_name="CoordinatorAgent",
                step=98,
                thought="Critical Resource Shortage",
                action="Failed to assign all required resources",
                alternatives={},
            )
        )

    forecast = result.get("forecast_warning")
    if forecast:
        db.add(
            AuditLog(
                incident_id=incident.id,
                agent_name="ForecastAgent",
                step=99,
                thought=forecast,
                action="forecast_warning",
                alternatives={},
            )
        )


async def create_incident_internal(
    db: AsyncSession,
    description: str,
    lat: float,
    lng: float,
    victims: int = 1,
) -> Incident:
    async with db.begin():
        incident = Incident(
            description=description,
            lat=lat,
            lng=lng,
            victims=victims,
            status="PENDING",
        )
        db.add(incident)
        await db.flush()
        incident_id = str(incident.id)

    initial_state = {
        "incident_id": incident_id,
        "raw_description": description,
        "incident_type": "other",
        "severity": "MEDIUM",
        "victims": victims,
        "specialty_required": "general",
        "location": (lat, lng),
        "minutes_waiting": 0.0,
        "trace": [],
    }

    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        print(f"[graph] run failed: {e}")
        result = initial_state

    async with db.begin():
        incident = await db.get(Incident, uuid.UUID(incident_id))
        if incident is None:
            raise HTTPException(status_code=500, detail="Incident lost during dispatch")
        await _persist_graph_result(db, incident, result)

    await invalidate_resource_cache()
    return await fetch_incident_detail(db, incident_id)


async def create_incident_with_assignments(
    db: AsyncSession,
    payload: IncidentCreate,
) -> Incident:
    return await create_incident_internal(
        db,
        description=payload.description,
        lat=payload.lat,
        lng=payload.lng,
    )


@router.post("", response_model=IncidentDetail, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
) -> Incident:
    return await create_incident_with_assignments(db, payload)


@router.get("", response_model=list[IncidentDetail])
async def list_incidents(
    status_filter: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Incident]:
    stmt = (
        select(Incident)
        .options(selectinload(Incident.assignments), selectinload(Incident.audit_logs))
        .order_by(Incident.created_at.desc())
    )
    if status_filter is not None:
        stmt = stmt.where(Incident.status == status_filter)
    if severity is not None:
        stmt = stmt.where(Incident.severity == severity)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{incident_id}", response_model=IncidentDetail)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
) -> Incident:
    return await fetch_incident_detail(db, incident_id)


@router.post("/simulate", response_model=IncidentDetail, status_code=status.HTTP_201_CREATED)
async def simulate_incident(
    payload: SimulateRequest,
    db: AsyncSession = Depends(get_db),
) -> Incident:
    scenarios = {
        "bus_accident": IncidentCreate(
            description="School bus crash near AIIMS, 15 children injured",
            lat=28.5672,
            lng=77.2100,
        ),
        "cardiac": IncidentCreate(
            description="Cardiac arrest near India Gate, 1 patient with chest pain",
            lat=28.6127,
            lng=77.2295,
        ),
        "building_fire": IncidentCreate(
            description="Building fire at Connaught Place, 8 people injured by smoke and burns",
            lat=28.6315,
            lng=77.2167,
        ),
    }
    scenario = scenarios.get(payload.scenario)
    if scenario is None:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown scenario: {payload.scenario}",
        )

    return await create_incident_with_assignments(db, scenario)


@router.post("/simulate/mass-casualty")
async def simulate_mass_casualty(bg: BackgroundTasks) -> dict[str, object]:
    from app.utils.demo_data import MASS_CASUALTY_SCENARIO

    async def fire_all() -> None:
        for step in MASS_CASUALTY_SCENARIO:
            await asyncio.sleep(step["delay_s"])
            async with async_session() as db:
                await create_incident_internal(
                    db,
                    description=step["description"],
                    lat=step["lat"],
                    lng=step["lng"],
                    victims=step["victims"],
                )

    bg.add_task(fire_all)
    return {"ok": True, "fired": len(MASS_CASUALTY_SCENARIO)}
