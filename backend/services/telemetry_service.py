import os
import logging
import pandas as pd
from datetime import datetime
from core.config import settings
from ai_engine.retraining_engine import RetrainingEngine

logger = logging.getLogger(__name__)


class TelemetryService:
    """
    Handles telemetry ingestion, validation, dataset updates,
    and retraining triggers
    """

    def __init__(self):

        self.dataset_path = os.path.join(
            settings.DATA_DIR,
            "training_dataset.csv"
        )

        self.retraining_engine = RetrainingEngine()

        # ensure data directory exists
        os.makedirs(settings.DATA_DIR, exist_ok=True)

    # ================================
    # Validation
    # ================================
    def _validate_payload(self, payload):

        required_fields = [
            "building_id",
            "temperature",
            "humidity",
            "occupancy",
            "day_of_week",
            "hour",
            "energy_usage_kwh"
        ]

        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing telemetry field: {field}")

        return True

    # ================================
    # Data normalization
    # ================================
    def _normalize_payload(self, payload):

        payload["timestamp"] = datetime.utcnow()

        return payload

    # ================================
    # Dataset append
    # ================================
    def _append_to_dataset(self, payload):

        df = pd.DataFrame([payload])

        if os.path.exists(self.dataset_path):
            df.to_csv(self.dataset_path, mode="a", header=False, index=False)
        else:
            df.to_csv(self.dataset_path, index=False)

    # ================================
    # Rolling dataset control
    # ================================
    def _enforce_dataset_limit(self, max_rows=500000):

        if not os.path.exists(self.dataset_path):
            return

        df = pd.read_csv(self.dataset_path)

        if len(df) > max_rows:
            df = df.tail(max_rows)
            df.to_csv(self.dataset_path, index=False)
            logger.info("Dataset trimmed to rolling window")

    # ================================
    # Retraining trigger logic
    # ================================
    def _should_trigger_retraining(self, rows_added):

        # simple policy: retrain every 10k new rows
        return rows_added >= 10000

    # ================================
    # Public ingest function
    # ================================
    def ingest_telemetry(self, payload):

        try:

            self._validate_payload(payload)

            payload = self._normalize_payload(payload)

            self._append_to_dataset(payload)

            self._enforce_dataset_limit()

            logger.info("Telemetry ingested successfully")

            return {"status": "ingested"}

        except Exception as e:
            logger.error(f"Telemetry ingestion failed: {e}")
            raise

    # ================================
    # Manual retraining trigger
    # ================================
    def trigger_retraining(self):

        logger.info("Manual retraining triggered")
        self.retraining_engine.retrain_models()

        return {"status": "retraining_started"}

    # ================================
    # Retrieve latest telemetry
    # ================================
    def get_latest(self):
        """
        Returns the most recent telemetry record from the rolling dataset.
        If no dataset exists, returns a sensible default telemetry payload.
        """

        try:
            if os.path.exists(self.dataset_path):
                df = pd.read_csv(self.dataset_path)
                if len(df) > 0:
                    latest = df.tail(1).to_dict(orient="records")[0]
                    # ensure timestamp present
                    latest.setdefault("timestamp", datetime.utcnow())
                    return latest

            # fallback default
            return {
                "building_id": 1,
                "temperature": 22.0,
                "humidity": 40.0,
                "occupancy": 0.1,
                "day_of_week": datetime.utcnow().weekday(),
                "hour": datetime.utcnow().hour,
                "energy_usage_kwh": 150.0,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Failed to load latest telemetry: {e}")
            return {
                "building_id": 1,
                "temperature": 22.0,
                "humidity": 40.0,
                "occupancy": 0.1,
                "day_of_week": datetime.utcnow().weekday(),
                "hour": datetime.utcnow().hour,
                "energy_usage_kwh": 150.0,
                "timestamp": datetime.utcnow()
            }

    def get_recent_dataset(self, max_rows: int = 500):
        """
        Returns a list of recent telemetry records (as dicts). If no dataset
        exists, returns an empty list.
        """

        try:
            if not os.path.exists(self.dataset_path):
                return []

            df = pd.read_csv(self.dataset_path)
            if df.empty:
                return []

            recent = df.tail(max_rows)
            return recent.to_dict(orient="records")

        except Exception:
            logger.exception("Failed to load recent dataset")
            return []
