"""
Centralised logging configuration.

Two handlers:
  - Console: INFO and above (progress + warnings + errors).
  - File:    DEBUG and above, saved to logs/run_<timestamp>.log.

Call `setup_logging()` once at the start of `main.py`.
"""
import logging
import os
from datetime import datetime


def setup_logging(log_dir='logs', level_console=logging.INFO, level_file=logging.DEBUG):
    """
    Configure root logger with console + timestamped file handlers.

    Parameters
    ----------
    log_dir : str
        Directory for log files (created if missing).
    level_console : int
        Minimum level for console output (default INFO).
    level_file : int
        Minimum level for file output (default DEBUG).
    """
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'run_{timestamp}.log')

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # lowest level; handlers filter further

    # Avoid duplicate handlers if setup_logging is called twice.
    if root.handlers:
        root.handlers.clear()

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level_console)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    # File handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(level_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    root.addHandler(console)
    root.addHandler(file_handler)

    logging.info(f"Logging initialised. File: {log_file}")