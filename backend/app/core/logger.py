"""
Logging Configuration
=====================
Structured logging system to replace print() statements.

WHY: 
    - Print statements clutter code and can't be controlled in production
    - Logging allows different levels (DEBUG, INFO, WARNING, ERROR)
    - Can enable/disable verbose logs via environment variable
    - Easier to trace issues with timestamps and module names

WHERE USED: Throughout the application for debugging and monitoring
HOW IT WORKS:
    1. Import: from app.core.logger import get_logger
    2. Create logger: logger = get_logger(__name__)
    3. Use: logger.info("message"), logger.error("error"), logger.debug("debug")
    
LOG LEVELS:
    - DEBUG: Detailed information for diagnosing problems (verbose)
    - INFO: General information about application flow
    - WARNING: Something unexpected but application continues
    - ERROR: Serious problem, feature may not work
"""

import logging
import sys
from .config import settings

# Create custom formatter for consistent log format
# FORMAT: timestamp - module - level - message
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    """
    Configure root logger for the application.
    
    WHY: Sets up logging once at application startup
    WHERE: Called from main.py during app initialization
    HOW: Configures handler, formatter, and log level from settings
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Set log level from configuration
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create console handler (outputs to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (use __name__ to auto-detect)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Starting process...")
        logger.debug("Variable value: %s", some_var)
        logger.error("Operation failed: %s", error)
    """
    return logging.getLogger(name)


# Configure logging on module import
setup_logging()
