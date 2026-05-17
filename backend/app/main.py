from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.database import initialize_database
from app.routers.energy_data import router as energy_data_router


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — allow all origins for this public read-only API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # ROOT ROUTE
    @app.get("/")
    def root():
        return {
            "message": "Public Energy and Climate Tracker API is running",
            "docs": "/docs",
        }

    # INCLUDE ROUTERS
    app.include_router(energy_data_router)  # routes: /energy-data, /historical-data, /daily-trends

    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix
    )

    # STARTUP EVENT
    @app.on_event("startup")
    def on_startup() -> None:
        initialize_database()

    return app


app = create_application()