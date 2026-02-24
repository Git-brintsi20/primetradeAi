"""Structured logging configuration for the trading bot."""
import logging
import os


def setup_logging(log_file: str = "app.log") -> logging.Logger:
    """Configure structured logging to both console and a log file.

    Args:
        log_file: Path to the log file (default: app.log).

    Returns:
        Root logger configured with both handlers.
    """
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers on repeated calls
    if not root_logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    return root_logger
