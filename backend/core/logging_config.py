import os
import logging
from logging.handlers import RotatingFileHandler
from core.config import settings


class LoggingConfig:
    """
    Centralized enterprise logging configuration.
    Provides:
    - rotating log files
    - separate error logs
    - console logging
    - service-wide logger initialization
    """

    @staticmethod
    def setup_logging():

        log_dir = os.path.join(settings.BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "application.log")
        error_log_file = os.path.join(log_dir, "errors.log")

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Error-only handler
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

        logging.info("Logging system initialized successfully")
