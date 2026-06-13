from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from sqlalchemy import select

from app.db import async_session
from app.models import Assignment, AuditLog, Incident, Resource

router = APIRouter(tags=["pdf"])


@router.get("/{incident_id}/pdf")
async def incident_pdf(incident_id: str):
    async with async_session() as s:
        inc = (
            await s.execute(select(Incident).where(Incident.id == incident_id))
        ).scalar_one_or_none()
        if not inc:
            raise HTTPException(status_code=404, detail="incident not found")
        assigns = (
            await s.execute(select(Assignment).where(Assignment.incident_id == inc.id))
        ).scalars().all()
        rid_to_name = dict((await s.execute(select(Resource.id, Resource.name))).all())
        logs = (
            await s.execute(
                select(AuditLog)
                .where(AuditLog.incident_id == inc.id)
                .order_by(AuditLog.step)
            )
        ).scalars().all()

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "CivicOS — Emergency Response Report")
    y -= 1 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Incident: {inc.description}")
    y -= 0.6 * cm
    c.drawString(
        2 * cm,
        y,
        f"Severity: {inc.severity}   Victims: {inc.victims}   "
        f"Type: {inc.type}   Status: {inc.status}",
    )
    y -= 0.6 * cm
    c.drawString(
        2 * cm,
        y,
        f"Created: {inc.created_at}   Priority: {inc.priority_score}",
    )
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Assignments")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    for a in assigns:
        c.drawString(
            2 * cm,
            y,
            f"• {a.role}: {rid_to_name.get(a.resource_id, '?')}  "
            f"ETA {a.eta_min} min  ({a.distance_km} km)",
        )
        y -= 0.5 * cm
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Reasoning Chain")
    y -= 0.6 * cm
    c.setFont("Helvetica", 9)
    for log in logs:
        c.drawString(
            2 * cm, y, f"[{log.agent_name} step {log.step}] {log.thought[:90]}"
        )
        y -= 0.45 * cm
        c.drawString(2.4 * cm, y, f"→ {log.action[:90]}")
        y -= 0.55 * cm
        if y < 2 * cm:
            c.showPage()
            y = h - 2 * cm
    c.save()
    pdf_bytes = buf.getvalue()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=incident_{incident_id}.pdf"},
    )
