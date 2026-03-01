"""
Logging System for cmdra AI
Provides centralized logging with file rotation and console output.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
import config


def setup_logger():
    """
    Setup application-wide logging system.
    
    Creates logs directory if it doesn't exist and configures:
    - File logging with rotation
    - Console logging for errors
    - Proper formatting
    """
    # Create logs directory if it doesn't exist
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.MAX_LOG_SIZE,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (errors only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logger.info("=" * 60)
    logger.info("cmdra AI Logging System Initialized")
    logger.info("=" * 60)
    
    return logger


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


