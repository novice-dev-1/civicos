from fastapi import APIRouter

from app.agents.forecast import forecast_agent

router = APIRouter(tags=["forecast"])


@router.get("/forecast")
async def forecast_endpoint():
    out = await forecast_agent({"trace": []})
    warning = out.get("forecast_warning")
    return {
        "warning": warning,
        "shortage_predicted": warning is not None,
        "shortage_in_min": None,
        "recommendations": [warning] if warning else [],
    }
