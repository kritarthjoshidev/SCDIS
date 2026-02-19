import numpy as np
import logging
from utils.model_loader import ModelLoader
from core.config import settings

logger = logging.getLogger(__name__)


class AnomalyEngine:
    """
    Detects abnormal energy usage patterns using anomaly detection model
    """

    def __init__(self):
        self.model = ModelLoader.load_anomaly_model()

    def detect(self, predicted_usage: float):
        """
        Detect anomaly based on predicted usage
        """

        try:
            value = np.array([[predicted_usage]])
            result = self.model.predict(value)[0]

            anomaly_flag = result == settings.ANOMALY_SCORE_THRESHOLD

            logger.info(f"Anomaly detection result: {result}")

            return {
                "anomaly_flag": anomaly_flag,
                "raw_score": int(result)
            }

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            raise
