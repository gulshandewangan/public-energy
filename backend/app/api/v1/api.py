from fastapi import APIRouter

from app.api.v1.endpoints import health, metrics

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

