import logging
import sys
import os
import datetime
from logging.handlers import RotatingFileHandler
from config import LOG_DIR

def setup_logger(log_dir=None):
    # Create logger
    logger = logging.getLogger('discord_bot')
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent messages from being passed to the root logger

    # Use configured log directory or fallback to /app/logs
    effective_log_dir = log_dir or LOG_DIR
    
    # Ensure log directory exists
    try:
        os.makedirs(effective_log_dir, exist_ok=True)
        log_file_path = os.path.join(effective_log_dir, 'discord_bot.log')
    except Exception as e:
        print(f"Failed to create log directory {effective_log_dir}: {e}")
        # Fallback to current directory
        log_file_path = 'discord_bot.log'

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    # Using RotatingFileHandler for size-based rotation
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5, encoding='utf-8')

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    # Check if handlers already exist to prevent duplicate logging
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    # Configure root logger to ensure all modules can log to console and file
    root_logger = logging.getLogger() # Gets the root logger
    root_logger.setLevel(logging.INFO)
    
    # Add a basic console handler to root logger for modules that don't have specific loggers
    # Check if handlers already exist to prevent duplicate logging
    if not root_logger.handlers:
        root_console_handler = logging.StreamHandler(sys.stdout)
        root_console_handler.setFormatter(formatter)
        root_logger.addHandler(root_console_handler)

    return logger

def clean_old_logs(log_dir, days_old=3):
    """
    Cleans up log files in the specified directory that are older than days_old.
    """
    # Use configured log directory if not specified
    effective_log_dir = log_dir or LOG_DIR
    
    if not effective_log_dir or not os.path.isdir(effective_log_dir):
        logging.getLogger('discord_bot').warning(f"Log directory '{effective_log_dir}' not found or invalid for cleanup.")
        return

    now = datetime.datetime.now()
    cutoff_time = now - datetime.timedelta(days=days_old)
    
    logger = logging.getLogger('discord_bot')
    logger.info(f"Starting log cleanup in '{effective_log_dir}'. Deleting files older than {days_old} days.")

    for filename in os.listdir(effective_log_dir):
        filepath = os.path.join(effective_log_dir, filename)
        if os.path.isfile(filepath) and filename.endswith('.log'):
            try:
                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                if mod_time < cutoff_time:
                    os.remove(filepath)
                    logger.info(f"Deleted old log file: {filepath}")
            except Exception as e:
                logger.error(f"Error deleting log file {filepath}: {e}")
    logger.info("Log cleanup finished.")