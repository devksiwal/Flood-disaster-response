from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.database.connection import init_db, engine
from app.database.seed import seed_database
from app.api.v1.auth import router as auth_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.agents import router as agents_router
from app.api.v1.teams import router as teams_router
from app.api.v1.flood_risk import router as flood_router
from app.api.v1.routes import router as routes_router
from app.api.v1.relief_camps import router as camps_router
from app.api.v1.events import router as events_router, ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and seed scenario dataset
    logger.info("Initializing National Flood Response Command System Backend...")
    await init_db()
    await seed_database()
    logger.info("System Ready. All 5 Multi-Agent modules operational.")
    yield
    # Shutdown: Clean up connections
    logger.info("Shutting down EOC backend services...")
    await engine.dispose()


app = FastAPI(
    title="Agentic AI Autonomous Flood Disaster Response System",
    description="Production-grade multi-agent disaster coordination platform powered by CrewAI and FastAPI.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local development and Docker network
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(teams_router, prefix=settings.API_V1_STR)
app.include_router(flood_router, prefix=settings.API_V1_STR)
app.include_router(routes_router, prefix=settings.API_V1_STR)
app.include_router(camps_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(events_router)  # Also expose /events/ws directly
app.include_router(ws_router)      # Expose /ws/events and /ws directly


@app.get("/")
async def root():
    return {
        "system": "National Disaster Management Authority (NDMA)",
        "project": "Agentic AI Based Autonomous Flood Disaster Response and Rescue Coordination System",
        "defcon_level": "SEVERITY_LEVEL_4_RED_ALERT",
        "status": "OPERATIONAL",
        "docs_url": "/docs",
        "active_agents": 5
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "agents": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
