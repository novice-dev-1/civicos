from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import Assignment, AuditLog, Incident, Resource
from app.routers.resources import invalidate_resource_cache


router = APIRouter(tags=["admin"])
settings = get_settings()


def require_admin(x_admin_token: str | None) -> None:
    if settings.admin_token:
        if x_admin_token != settings.admin_token:
            raise HTTPException(status_code=401, detail="invalid admin token")


@router.post("/reset")
async def reset_city(
    confirm: bool = False,
    x_admin_token: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    if not confirm:
        raise HTTPException(status_code=400, detail="Pass ?confirm=true to reset")
    require_admin(x_admin_token)

    async with db.begin():
        await db.execute(delete(AuditLog))
        await db.execute(delete(Assignment))
        await db.execute(delete(Incident))
        await db.execute(
            update(Resource).values(capacity_used=0, status="AVAILABLE")
        )

    await invalidate_resource_cache()
    return {"reset": True, "timestamp": datetime.now(UTC).isoformat()}
