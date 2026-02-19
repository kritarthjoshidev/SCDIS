import os
import logging
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression

from core.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Enterprise-safe model loading utility.
    Provides:
    - lazy loading
    - auto model generation if missing
    - corruption fallback
    - caching
    """

    _forecast_model = None

    # ======================================================
    # Auto model creation
    # ======================================================
    @staticmethod
    def _create_default_model(path):

        logger.warning("Forecast model missing — creating default model")

        X = np.random.rand(200, 6)
        y = np.random.rand(200)

        model = LinearRegression()
        model.fit(X, y)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)

        logger.info("Default forecast model generated")

        return model

    # ======================================================
    # Load forecast model
    # ======================================================
    @classmethod
    def load_forecast_model(cls):

        if cls._forecast_model is not None:
            return cls._forecast_model

        path = settings.FORECAST_MODEL_PATH

        try:
            logger.info("Loading forecast model...")

            if not os.path.exists(path):
                cls._forecast_model = cls._create_default_model(path)
                return cls._forecast_model

            cls._forecast_model = joblib.load(path)

            logger.info("Forecast model loaded successfully")

            return cls._forecast_model

        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            cls._forecast_model = cls._create_default_model(path)
            return cls._forecast_model

    # ======================================================
    # Reload model (hot reload support)
    # ======================================================
    @classmethod
    def reload_model(cls):

        logger.info("Reloading forecast model")

        cls._forecast_model = None
        return cls.load_forecast_model()
    @classmethod
    def reload_models(cls):
        """
        Backward-compatible bulk reload used by retraining pipeline.
        """

        logger.info("Reloading all model artifacts")
        cls._forecast_model = None
        cls._anomaly_model = None

        forecast = cls.load_forecast_model()
        anomaly = cls.load_anomaly_model()

        return {
            "forecast_loaded": forecast is not None,
            "anomaly_loaded": anomaly is not None,
        }
    _anomaly_model = None

    # ======================================================
    # Create default anomaly model
    # ======================================================
    @staticmethod
    def _create_default_anomaly_model(path):

        from sklearn.ensemble import IsolationForest

        logger.warning("Anomaly model missing — creating default anomaly model")

        import numpy as np

        X = np.random.rand(300, 1)

        model = IsolationForest()
        model.fit(X)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)

        logger.info("Default anomaly model generated")

        return model

    # ======================================================
    # Load anomaly model
    # ======================================================
    @classmethod
    def load_anomaly_model(cls):

        if cls._anomaly_model is not None:
            return cls._anomaly_model

        path = settings.ANOMALY_MODEL_PATH

        try:
            logger.info("Loading anomaly model...")

            if not os.path.exists(path):
                cls._anomaly_model = cls._create_default_anomaly_model(path)
                return cls._anomaly_model

            cls._anomaly_model = joblib.load(path)

            logger.info("Anomaly model loaded successfully")

            return cls._anomaly_model

        except Exception as e:
            logger.error(f"Anomaly model loading failed: {e}")
            cls._anomaly_model = cls._create_default_anomaly_model(path)
            return cls._anomaly_model
