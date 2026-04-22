import logging
from pathlib import Path
logger = logging.getLogger(__name__)

def setup_logging(log_filepath: Path):
    """Configures logging to both console and the specified file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-30s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler()
        ]
    )
    # Return the root logger or a specific one
    return logging.getLogger(__name__)


def print_log_separator(message: str) -> None:
    """Prints Uppercase section header to log"""
    logger.info("=" * 60)
    logger.info(message.upper())
    logger.info("=" * 60)
