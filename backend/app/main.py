from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.routers import admin, counterfactual, events, forecast, incidents, kpi, pdf, resources


settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


app.include_router(resources.router, prefix="/resources")
app.include_router(incidents.router, prefix="/incidents")
app.include_router(kpi.router, prefix="/kpi")
app.include_router(admin.router, prefix="/admin")
app.include_router(events.router)
app.include_router(counterfactual.router)
app.include_router(forecast.router)
app.include_router(pdf.router, prefix="/incidents")


@app.on_event("startup")
async def startup() -> None:
    if not settings.admin_token and settings.environment != "dev":
        logger.warning("ADMIN_TOKEN is unset — /admin/reset is unprotected")
    await resources.warm_resource_cache()
