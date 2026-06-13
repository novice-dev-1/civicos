import asyncio
import logging
import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal, get_db
from app.models import Resource
from app.schemas import ResourceOut


router = APIRouter(tags=["resources"])
logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 300
_resource_cache: list[ResourceOut] | None = None
_resource_cache_loaded_at = 0.0
_resource_cache_lock = asyncio.Lock()


async def _load_resources_from_db(db: AsyncSession) -> list[ResourceOut]:
    started_at = time.perf_counter()
    result = await db.execute(select(Resource).order_by(Resource.type, Resource.name))
    resources = [ResourceOut.model_validate(resource) for resource in result.scalars().all()]
    elapsed = time.perf_counter() - started_at
    logger.info("Loaded %s resources from database in %.2fs", len(resources), elapsed)
    return resources


async def get_cached_resources(db: AsyncSession, force: bool = False) -> list[ResourceOut]:
    global _resource_cache, _resource_cache_loaded_at

    now = time.monotonic()
    if (
        not force
        and _resource_cache is not None
        and now - _resource_cache_loaded_at < _CACHE_TTL_SECONDS
    ):
        return _resource_cache

    async with _resource_cache_lock:
        now = time.monotonic()
        if (
            not force
            and _resource_cache is not None
            and now - _resource_cache_loaded_at < _CACHE_TTL_SECONDS
        ):
            return _resource_cache

        _resource_cache = await _load_resources_from_db(db)
        _resource_cache_loaded_at = time.monotonic()
        return _resource_cache


async def warm_resource_cache() -> None:
    async with AsyncSessionLocal() as db:
        await get_cached_resources(db, force=True)


async def invalidate_resource_cache() -> None:
    global _resource_cache, _resource_cache_loaded_at

    async with _resource_cache_lock:
        _resource_cache = None
        _resource_cache_loaded_at = 0.0


@router.get("", response_model=list[ResourceOut])
async def list_resources(
    resource_type: str | None = Query(
        default=None,
        alias="type",
        pattern="^(ambulance|hospital|police)$",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[ResourceOut]:
    resources = await get_cached_resources(db)
    if resource_type is not None:
        return [resource for resource in resources if resource.type == resource_type]

    return resources


@router.get("/load")
async def resources_load(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(
        select(Resource).where(Resource.type == "hospital").order_by(Resource.name)
    )
    rows = result.scalars().all()
    return [
        {
            "name": r.name,
            "used": r.capacity_used or 0,
            "total": r.capacity_total or 1,
            "ratio": round((r.capacity_used or 0) / (r.capacity_total or 1), 2),
        }
        for r in rows
    ]
