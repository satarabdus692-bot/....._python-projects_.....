"""JARVIS Logger — persists session logs to file."""

import os
import logging
from datetime import datetime
from pathlib import Path


class JarvisLogger:
    def __init__(self):
        log_dir = Path.home() / "jarvis_downloads" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            filename=str(log_file),
            level=logging.DEBUG,
            format="%(asctime)s  %(levelname)-8s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self._logger = logging.getLogger("jarvis")

    def log(self, msg: str):
        self._logger.info(msg)

    def error(self, msg: str):
        self._logger.error(msg)
        print(f"  [LOG] Error recorded: {msg}")

    def warn(self, msg: str):
        self._logger.warning(msg)
