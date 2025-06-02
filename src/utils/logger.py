import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import os

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with file rotation and console output.
    
    Args:
        name (str): Logger name
        log_file (str, optional): Log file path
        level (int): Logging level
        console_output (bool): Whether to output to console
        max_bytes (int): Maximum log file size before rotation
        backup_count (int): Number of backup files to keep
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set logging level
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler with rotation if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_scraper_logger(scraper_type: str = "basic") -> logging.Logger:
    """
    Get a pre-configured logger for scraper operations.
    
    Args:
        scraper_type (str): Type of scraper ('basic' or 'selenium')
        
    Returns:
        logging.Logger: Configured logger
    """
    log_file = f"logs/{scraper_type}_scraper.log"
    logger_name = f"linkedin_scraper.{scraper_type}"
    
    return setup_logger(
        name=logger_name,
        log_file=log_file,
        level=logging.INFO,
        console_output=True
    ) 