import logging
import sys
from pathlib import Path

from music_master.config import Config


def setup_logging(config: Config) -> None:
    """Configures application-wide logging."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    level = getattr(logging, config.log_level.upper(), logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if config.log_to_file and config.log_file_path:
        log_file = Path(config.log_file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(log_file), encoding="utf-8"))

    logging.basicConfig(level=level, format=log_format, handlers=handlers, force=True)
