"""
Logging and provenance tracking utility for reproducible research.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_dir: Path = None, level: int = logging.INFO) -> logging.Logger:
    """Configures a standardized console and file logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler if requested
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fh = logging.FileHandler(log_dir / f"{name}_{timestamp}.log", encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            
    return logger
