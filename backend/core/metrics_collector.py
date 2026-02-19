import logging
import time
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Central observability and AI performance monitoring system.
    Tracks:
    - inference latency
    - anomaly frequency
    - retraining frequency
    - system uptime
    - pipeline execution metrics
    """

    def __init__(self):

        self.start_time = datetime.utcnow()

        self.inference_latencies: List[float] = []
        self.anomaly_events = 0
        self.total_predictions = 0
        self.retraining_runs = 0
        self.pipeline_runs = 0

    # ==========================================
    # Inference latency tracking
    # ==========================================
    def record_inference_latency(self, latency: float):

        self.inference_latencies.append(latency)
        self.total_predictions += 1

    # ==========================================
    # Anomaly tracking
    # ==========================================
    def record_anomaly(self):

        self.anomaly_events += 1

    # ==========================================
    # Retraining tracking
    # ==========================================
    def record_retraining(self):

        self.retraining_runs += 1

    # ==========================================
    # Pipeline execution tracking
    # ==========================================
    def record_pipeline_run(self):

        self.pipeline_runs += 1

    # ==========================================
    # Compute averages
    # ==========================================
    def _average_latency(self):

        if not self.inference_latencies:
            return 0

        return round(
            sum(self.inference_latencies) / len(self.inference_latencies),
            4
        )

    # ==========================================
    # Drift indicator
    # ==========================================
    def compute_anomaly_rate(self):

        if self.total_predictions == 0:
            return 0

        return round(
            self.anomaly_events / self.total_predictions,
            4
        )

    # ==========================================
    # Uptime calculation
    # ==========================================
    def system_uptime_seconds(self):

        return (datetime.utcnow() - self.start_time).total_seconds()

    # ==========================================
    # Export metrics snapshot
    # ==========================================
    def export_metrics(self) -> Dict:

        metrics = {
            "timestamp": datetime.utcnow(),
            "avg_inference_latency": self._average_latency(),
            "total_predictions": self.total_predictions,
            "anomaly_events": self.anomaly_events,
            "anomaly_rate": self.compute_anomaly_rate(),
            "retraining_runs": self.retraining_runs,
            "pipeline_runs": self.pipeline_runs,
            "uptime_seconds": self.system_uptime_seconds()
        }

        logger.info("Metrics snapshot exported")

        return metrics
