"""
Usage:
    from backend.logger import logger
    logger.info("Something happened")
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory
LOG_DIR = Path(r"C:\Users\rocca\PycharmProjects\PythonPHMS\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


PROJECT_ROOT = Path(r"C:\Users\rocca\PycharmProjects\PythonPHMS")


class RelativePathFormatter(logging.Formatter):
    def format(self, record):
        pathname = Path(record.pathname)
        try:
            relative_path = pathname.relative_to(PROJECT_ROOT)
            record.pathname = str(relative_path)
        except ValueError:
            # If path is not under project root, keep original
            pass
        return super().format(record)

formatter = RelativePathFormatter(
    '%(asctime)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s'
)

file_handler = RotatingFileHandler(
    LOG_DIR / "pythonphms.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger("pythonphms")
__all__ = ["logger"]