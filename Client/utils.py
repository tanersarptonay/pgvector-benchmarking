import logging
from datetime import datetime

def setup_logger(name, log_file=None):
    """Set up a shared logger."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # For preventing duplicate handlers
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Log file
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    return logger
