from fastapi import APIRouter, HTTPException
import threading
import logging
from datetime import datetime

from presentation.demo_mode import DemoModeEngine

router = APIRouter(prefix="/demo", tags=["Demo Control"])
logger = logging.getLogger(__name__)

demo_engine = DemoModeEngine()
demo_thread = None


# ==================================================
# Start demo simulation
# ==================================================
@router.post("/start")
def start_demo(interval_seconds: int = 5):

    global demo_thread

    if demo_engine.running:
        return {"status": "already_running"}

    try:
        demo_thread = threading.Thread(
            target=demo_engine.start_demo,
            args=(interval_seconds,),
            daemon=True
        )
        demo_thread.start()

        return {
            "status": "demo_started",
            "interval_seconds": interval_seconds,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Demo start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Stop demo simulation
# ==================================================
@router.post("/stop")
def stop_demo():

    if not demo_engine.running:
        return {"status": "not_running"}

    demo_engine.stop_demo()

    return {
        "status": "demo_stopped",
        "timestamp": datetime.utcnow()
    }


# ==================================================
# Get recent demo outputs
# ==================================================
@router.get("/results")
def get_demo_results(limit: int = 10):

    try:
        results = demo_engine.get_recent_results(limit)

        return {
            "status": "success",
            "count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Demo results fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Demo status
# ==================================================
@router.get("/status")
def demo_status():

    return {
        "running": demo_engine.running,
        "timestamp": datetime.utcnow()
    }
