"""
Monitoring Routes
Provides system observability, AI health, drift status and performance metrics
"""

import logging
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from core.config import settings
from services.data_drift_monitor import DataDriftMonitor
from ai_engine.retraining_engine import RetrainingEngine
from ml_pipeline.model_registry import ModelRegistry
from services.laptop_runtime_service import laptop_runtime_service
from utils.model_loader import ModelLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

drift_monitor = DataDriftMonitor()
retraining_engine = RetrainingEngine()
model_registry = ModelRegistry()

VALID_LOG_SOURCES = {"application", "errors"}
VALID_MODEL_EXPORTS = {"forecast", "anomaly"}


def _tail_lines(file_path: Path, line_count: int):
    buffer = deque(maxlen=max(1, line_count))
    with file_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            buffer.append(line.rstrip("\n"))
    return list(buffer)


# -------------------------------------------------------------
# SYSTEM HEALTH
# -------------------------------------------------------------
@router.get("/system-health")
async def system_health():
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "drift_monitor": "OK",
                "retraining_engine": "OK",
                "model_registry": "OK"
            }
        }
    except Exception as e:
        logger.exception("System health endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# DRIFT STATUS
# -------------------------------------------------------------
@router.get("/data-drift-status")
async def data_drift_status():
    try:
        return drift_monitor.health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# TRIGGER DRIFT CHECK
# -------------------------------------------------------------
@router.post("/trigger-drift-check")
async def trigger_drift_check():
    try:
        result = drift_monitor.run_drift_check()
        return {"status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# MODEL PERFORMANCE
# -------------------------------------------------------------
@router.get("/model-performance")
async def model_performance():
    try:
        perf = model_registry.get_latest_model_performance()
        return {"performance": perf}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# RETRAINING STATUS
# -------------------------------------------------------------
@router.get("/retraining-status")
async def retraining_status():
    try:
        return retraining_engine.pipeline_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# AI PIPELINE HEALTH
# -------------------------------------------------------------
@router.get("/ai-pipeline-health")
async def ai_pipeline_health():
    return {
        "forecast_engine": "OK",
        "rl_engine": "OK",
        "optimization_engine": "OK",
        "reward_engine": "OK",
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------
# DRIFT HISTORY
# -------------------------------------------------------------
@router.get("/drift-history")
async def drift_history():
    try:
        history = getattr(drift_monitor, "drift_history", [])
        return {"history": history[-50:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# FORCE MODEL REGISTRY REFRESH
# -------------------------------------------------------------
@router.post("/refresh-model-registry")
async def refresh_model_registry():
    try:
        model_registry.refresh_registry()
        return {"status": "model registry refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# LIVE LAPTOP DASHBOARD PAYLOAD
# -------------------------------------------------------------
@router.get("/laptop/live-dashboard")
async def live_laptop_dashboard():
    try:
        return laptop_runtime_service.latest_payload(history_limit=30, event_limit=30, alert_limit=10)
    except Exception as e:
        logger.exception("Laptop live dashboard failed")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# LIVE LAPTOP STATUS
# -------------------------------------------------------------
@router.get("/laptop/status")
async def live_laptop_status():
    try:
        return laptop_runtime_service.health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# AUTO APPLY TOGGLE
# -------------------------------------------------------------
@router.post("/laptop/auto-apply")
async def laptop_auto_apply(payload: Dict[str, Any]):
    try:
        enabled = bool(payload.get("enabled", True))
        laptop_runtime_service.set_auto_apply(enabled)
        return {
            "status": "updated",
            "auto_apply_power_profile": enabled,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# RUNTIME MODE (LIVE_EDGE/SIMULATION/HYBRID)
# -------------------------------------------------------------
@router.post("/laptop/mode")
async def laptop_runtime_mode(payload: Dict[str, Any]):
    try:
        mode = str(payload.get("mode", "LIVE_EDGE"))
        laptop_runtime_service.set_mode(mode)
        return {
            "status": "updated",
            "mode": mode.upper(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# SCENARIO CONTROL
# -------------------------------------------------------------
@router.post("/laptop/scenario")
async def laptop_scenario(payload: Dict[str, Any]):
    try:
        scenario = str(payload.get("scenario", "normal"))
        cycles = int(payload.get("cycles", 12))
        laptop_runtime_service.set_scenario(scenario, cycles=cycles)
        return {
            "status": "updated",
            "scenario": scenario.lower(),
            "cycles": cycles,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# AI MODELS: MANUAL RETRAIN
# -------------------------------------------------------------
@router.post("/ai-models/retrain")
async def retrain_ai_models():
    try:
        result = retraining_engine.run_retraining_pipeline()
        return {
            "status": result.get("status", "completed"),
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.exception("AI model retraining endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# AI MODELS: VIEW LOGS
# -------------------------------------------------------------
@router.get("/ai-models/logs")
async def ai_model_logs(
    source: str = Query(default="application"),
    lines: int = Query(default=150, ge=20, le=1000),
):
    normalized_source = str(source).strip().lower()
    if normalized_source not in VALID_LOG_SOURCES:
        raise HTTPException(status_code=400, detail=f"Unsupported log source: {source}")

    log_path = Path(settings.LOG_DIR) / f"{normalized_source}.log"
    if not log_path.exists():
        raise HTTPException(status_code=404, detail=f"Log file not found: {log_path}")

    try:
        log_lines = _tail_lines(log_path, lines)
        return {
            "status": "ok",
            "source": normalized_source,
            "path": str(log_path),
            "line_count": len(log_lines),
            "lines": log_lines,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.exception("AI model log view failed")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# AI MODELS: EXPORT WEIGHTS
# -------------------------------------------------------------
@router.get("/ai-models/export-weights")
async def export_ai_model_weights(model: str = Query(default="forecast")):
    normalized_model = str(model).strip().lower()
    if normalized_model not in VALID_MODEL_EXPORTS:
        raise HTTPException(status_code=400, detail=f"Unsupported model export target: {model}")

    if normalized_model == "anomaly":
        ModelLoader.load_anomaly_model()
        model_path = Path(settings.ANOMALY_MODEL_PATH)
    else:
        ModelLoader.load_forecast_model()
        model_path = Path(settings.FORECAST_MODEL_PATH)

    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Model file not found: {model_path}")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{normalized_model}_model_weights_{timestamp}{model_path.suffix or '.pkl'}"

    return FileResponse(
        path=str(model_path),
        media_type="application/octet-stream",
        filename=filename,
    )
