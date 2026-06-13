from __future__ import annotations

import argparse
import asyncio
import random

from sqlalchemy import delete, func, select

from app.db import AsyncSessionLocal
from app.models import Resource


HOSPITALS = [
    ("AIIMS Delhi", 28.5672, 77.2100, 50, "trauma"),
    ("Safdarjung Hospital", 28.5687, 77.2053, 40, "trauma"),
    ("RML Hospital", 28.6280, 77.2070, 30, "general"),
    ("LNJP Hospital", 28.6406, 77.2381, 35, "general"),
    ("Max Saket", 28.5275, 77.2157, 25, "cardiac"),
    ("Apollo Delhi", 28.5421, 77.2849, 30, "cardiac"),
    ("Fortis Vasant Kunj", 28.5225, 77.1572, 20, "cardiac"),
    ("BLK Hospital", 28.6450, 77.1880, 22, "general"),
]

DELHI_LAT_RANGE = (28.55, 28.72)
DELHI_LNG_RANGE = (77.10, 77.30)
AMBULANCE_EQUIPMENT = ["defibrillator", "oxygen", "IV", "pediatric_kit"]
POLICE_ZONES = ["Central", "South", "East", "West", "North"]


def random_coordinate(rng: random.Random) -> tuple[float, float]:
    lat = rng.uniform(*DELHI_LAT_RANGE)
    lng = rng.uniform(*DELHI_LNG_RANGE)
    return round(lat, 6), round(lng, 6)


def build_resources() -> list[Resource]:
    rng = random.Random(42)
    resources: list[Resource] = []

    for name, lat, lng, capacity, specialty in HOSPITALS:
        resources.append(
            Resource(
                type="hospital",
                name=name,
                lat=lat,
                lng=lng,
                capacity_total=capacity,
                capacity_used=0,
                specialty=specialty,
                status="AVAILABLE",
            )
        )

    for index in range(1, 13):
        lat, lng = random_coordinate(rng)
        equipment_count = rng.randint(1, len(AMBULANCE_EQUIPMENT))
        resources.append(
            Resource(
                type="ambulance",
                name=f"A{index}",
                lat=lat,
                lng=lng,
                capacity_total=1,
                capacity_used=0,
                equipment=rng.sample(AMBULANCE_EQUIPMENT, equipment_count),
                status="AVAILABLE",
            )
        )

    for index in range(1, 11):
        lat, lng = random_coordinate(rng)
        resources.append(
            Resource(
                type="police",
                name=f"P{index}",
                lat=lat,
                lng=lng,
                capacity_total=1,
                capacity_used=0,
                jurisdiction=POLICE_ZONES[(index - 1) % len(POLICE_ZONES)],
                status="AVAILABLE",
            )
        )

    return resources


async def seed_resources(reset: bool = False) -> int:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            if reset:
                await session.execute(delete(Resource))

            existing_count = await session.scalar(select(func.count()).select_from(Resource))
            if existing_count:
                return int(existing_count)

            resources = build_resources()
            session.add_all(resources)
            return len(resources)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed JIRACHI Delhi resources.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing resources before seeding.",
    )
    args = parser.parse_args()

    count = await seed_resources(reset=args.reset)
    print(f"resources={count}")


if __name__ == "__main__":
    asyncio.run(main())
