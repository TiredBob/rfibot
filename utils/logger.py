import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir=None):
    # Create logger
    logger = logging.getLogger('discord_bot')
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent messages from being passed to the root logger

    # Determine log file path
    log_file_path = 'discord_bot.log'
    if log_dir:
        import os
        log_file_path = os.path.join(log_dir, log_file_path)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5, encoding='utf-8')

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Configure root logger to ensure all modules can log to console and file
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add a basic console handler to root logger for modules that don't have specific loggers
    root_console_handler = logging.StreamHandler(sys.stdout)
    root_console_handler.setFormatter(formatter)
    root_logger.addHandler(root_console_handler)

    return logger
