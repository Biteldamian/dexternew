# utils/logger.py
import logging
from rich.logging import RichHandler
from pathlib import Path

def setup_logger(name: str = "DexterGPT"):
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RichHandler(rich_tracebacks=True),
            logging.FileHandler(f"logs/dextergpt.log")
        ]
    )
    
    return logging.getLogger(name)

logger = setup_logger()