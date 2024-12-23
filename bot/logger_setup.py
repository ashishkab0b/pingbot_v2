import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Define log directory based on the script name
    script_name = Path(sys.argv[0]).stem
    log_dir = Path(f'logs/{script_name}')
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create a logger
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers
    if not logger.hasHandlers():
        # Rotating file handler
        file_handler = RotatingFileHandler(log_dir / 'all.log', maxBytes=10*1024*1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - Called by %(module)s - %(message)s"
        )
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")

        # Add formatters to handlers
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger