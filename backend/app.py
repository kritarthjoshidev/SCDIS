from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Routers
from routes.decision import router as decision_router

# ==========================
# Logging setup
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger("SCDIS")


# ==========================
# FastAPI App
# ==========================
app = FastAPI(
    title="Smart Campus Decision Intelligence System",
    version="2.0",
    description="AI-powered campus energy decision intelligence backend"
)


# ==========================
# CORS configuration
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
# Register routers
# ==========================
app.include_router(decision_router)


# ==========================
# Startup event
# ==========================
@app.on_event("startup")
async def startup_event():
    logger.info("SCDIS backend started successfully")


# ==========================
# Health check endpoint
# ==========================
@app.get("/")
def root():
    return {"message": "SCDIS AI backend running"}

from routes.monitoring import router as monitoring_router
app.include_router(monitoring_router)

from routes.orchestrator import router as orchestrator_router
app.include_router(orchestrator_router)

from scheduler import AutonomousScheduler

scheduler = AutonomousScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.start()

from routes.admin import router as admin_router
app.include_router(admin_router)

from routes.demo import router as demo_router
app.include_router(demo_router)

from routes.autonomous_ai import router as autonomous_ai_router
app.include_router(autonomous_ai_router)

from core.logging_config import LoggingConfig
LoggingConfig.setup_logging()

from core.enterprise_autonomous_bootstrap import enterprise_autonomous_bootstrap
from services.laptop_runtime_service import laptop_runtime_service

@app.on_event("startup")
async def startup_event():
    enterprise_autonomous_bootstrap.start()


@app.on_event("startup")
def start_laptop_runtime():
    laptop_runtime_service.start()
