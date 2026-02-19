"""
Decision Intelligence Routes

Provides:
- Real-time decision generation
- Batch decision simulation
- Decision health monitoring
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from ai_engine.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/decision", tags=["Decision Intelligence"])

decision_engine = DecisionEngine()

# ---------------------------------------------------------
# REAL-TIME DECISION
# ---------------------------------------------------------
@router.post("/generate")
async def generate_decision(payload: Dict[str, Any]):
    """
    Generates decision using real telemetry data
    """

    try:
        result = decision_engine.generate_decision(payload)

        return {
            "status": "success",
            "decision": result
        }

    except Exception as e:
        logger.exception("Decision generation failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# BATCH DECISION SIMULATION
# ---------------------------------------------------------
@router.post("/simulate-batch")
async def simulate_batch(data: List[Dict[str, Any]]):
    """
    Runs decision engine on multiple telemetry records
    """

    try:
        results = []

        for record in data:
            decision = decision_engine.generate_decision(record)
            results.append(decision)

        return {
            "status": "completed",
            "records_processed": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# DECISION ENGINE HEALTH
# ---------------------------------------------------------
@router.get("/health")
async def decision_health():
    """
    Returns decision engine health status
    """

    try:
        return {
            "timestamp": datetime.utcnow(),
            "engine_status": decision_engine.health_status(),
            "status": "healthy"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# QUICK TEST DECISION
# ---------------------------------------------------------
@router.get("/test")
async def test_decision():
    """
    Generates decision using mock telemetry
    Useful for testing pipeline quickly
    """

    try:
        mock_data = {
            "current_load": 450,
            "temperature": 32,
            "humidity": 65,
            "occupancy": 720
        }

        decision = decision_engine.generate_decision(mock_data)

        return {
            "status": "test_success",
            "decision": decision
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
