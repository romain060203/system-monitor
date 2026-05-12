# utils.py
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "monitor.log")

def setup_logging(level=logging.INFO, max_bytes=5*1024*1024, backup_count=3):
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler = RotatingFileHandler(LOG_FILE, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    # also log to console
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
