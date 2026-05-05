import logging
from pathlib import Path
logger = logging.getLogger(__name__)

def setup_logging(log_filepath: Path):
    """Configures logging to both console and the specified file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-30s | %(funcName)-25s:%(lineno)-3d | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def print_log_separator(message: str) -> None:
    """Prints Uppercase section header to log"""
    number_of_equals_chars = 80
    logger.info("=" * number_of_equals_chars)
    logger.info(message.upper())
    logger.info("=" * number_of_equals_chars)
