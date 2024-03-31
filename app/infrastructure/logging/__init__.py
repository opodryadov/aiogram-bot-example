import logging
import sys

from loguru import logger

from app.config import config
from app.infrastructure.logging.handler import InterceptHandler


def setup_logging() -> None:
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(config.logging_level)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(handlers=[{"sink": sys.stdout, "serialize": False}])
