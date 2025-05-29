import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(debug=False, config_manager=None):
    """
    Setup unified logging configuration for the application.
    
    Args:
        debug (bool): If True, set logging level to DEBUG
        config_manager (ConfigManager): Optional ConfigManager instance
    
    Returns:
        logging.Logger: Root logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Get logging config from config manager if available
    max_size_mb = 10
    backup_count = 5
    if config_manager:
        logging_config = config_manager.get("logging", {})
        max_size_mb = logging_config.get("max_size_mb", 10)
        backup_count = logging_config.get("backup_count", 5)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(
                logs_dir, 
                f"app_{datetime.now().strftime('%Y%m%d')}.log"
            ),
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    except Exception as e:
        # CRITICAL FIX: Return logger object, not None
        print(f"Error setting up file logging: {e}")
        
        # At minimum, set up console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger  # Always return logger object, never None
