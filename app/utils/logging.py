import logging

import pythonjsonlogger

from app.config import settings


def setup_logging():
    handler = logging.StreamHandler()
    log_formatter = pythonjsonlogger.json.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"}
    )
    handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    logger.handlers.clear()
    logger.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
