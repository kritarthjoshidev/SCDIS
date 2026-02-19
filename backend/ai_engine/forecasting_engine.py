import numpy as np
import logging
from utils.model_loader import ModelLoader
from core.config import settings

logger = logging.getLogger(__name__)


class ForecastingEngine:
    """
    AI Forecasting Engine
    Responsible for predicting campus energy demand
    """

    def __init__(self):
        self.model = ModelLoader.load_forecast_model()

    def _prepare_features(self, data: dict):
        """
        Prepare input features for model inference
        """

        try:
            features = np.array([[
                data["building_id"],
                data["temperature"],
                data["humidity"],
                data["occupancy"],
                data["day_of_week"],
                data["hour"]
            ]])

            return features

        except KeyError as e:
            logger.error(f"Missing feature: {e}")
            raise

    def forecast(self, data: dict):
        """
        Perform energy usage prediction
        """

        features = self._prepare_features(data)

        prediction = self.model.predict(features)[0]

        logger.info(f"Forecast generated: {prediction}")

        return {
            "predicted_energy_usage": float(prediction),
            "threshold": settings.HIGH_USAGE_THRESHOLD,
            "high_usage_flag": bool(prediction > settings.HIGH_USAGE_THRESHOLD)
        }

    # compatibility alias used across codebase
    def predict(self, data: dict):
        return self.forecast(data)
