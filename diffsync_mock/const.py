"""Module-wide variables to be used throughout the project."""
import logging

from pathlib import Path

logging.basicConfig(level=logging.INFO)

REDIS_PORT = 7379
REDIS_HOST = "localhost"
LOGGER = logging.getLogger("example#5")


DIR_PATH = Path(__file__).parent.absolute()
LOCAL_FILE_NAME = f"{DIR_PATH}/local_adapter.json"

DEFAULT_RECORDS = 20000
