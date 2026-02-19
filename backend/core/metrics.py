from fastapi import APIRouter
import logging
from datetime import datetime

from core.metrics_collector import MetricsCollector

router = APIRouter(prefix="/metrics", tags=["Metrics"])
logger = logging.getLogger(__name__)

metrics_collector = MetricsCollector()


# ==========================================
# System metrics
# ==========================================
@router.get("/system")
def system_metrics():

    metrics = metrics_collector.export_metrics()

    return {
        "type": "system_metrics",
        "timestamp": datetime.utcnow(),
        "data": metrics
    }


# ==========================================
# Inference metrics
# ==========================================
@router.get("/inference")
def inference_metrics():

    metrics = {
        "avg_latency": metrics_collector._average_latency(),
        "total_predictions": metrics_collector.total_predictions,
        "anomaly_rate": metrics_collector.compute_anomaly_rate()
    }

    return {
        "type": "inference_metrics",
        "timestamp": datetime.utcnow(),
        "data": metrics
    }


# ==========================================
# Pipeline metrics
# ==========================================
@router.get("/pipeline")
def pipeline_metrics():

    metrics = {
        "pipeline_runs": metrics_collector.pipeline_runs,
        "retraining_runs": metrics_collector.retraining_runs
    }

    return {
        "type": "pipeline_metrics",
        "timestamp": datetime.utcnow(),
        "data": metrics
    }


# ==========================================
# Health snapshot
# ==========================================
@router.get("/health")
def health_snapshot():

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
