import logging
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class TacticalFormatter(logging.Formatter):
    """Custom color-coded terminal formatter for National EOC logs."""
    
    GREY = "\x1b[38;20m"
    CYAN = "\x1b[36;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: CYAN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str = "flood_response") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(TacticalFormatter())
        logger.addHandler(handler)
    return logger


logger = setup_logger()


def log_agent_step(agent_name: str, step: str, thought: str, action: str, details: Optional[Dict[str, Any]] = None):
    """Log structured agent steps for audit trails and terminal output."""
    timestamp = datetime.now(timezone.utc).isoformat()
    msg = f"AGENT [{agent_name}] -> Step: '{step}' | Thought: {thought} | Action: {action}"
    logger.info(msg)
    return {
        "timestamp": timestamp,
        "agent": agent_name,
        "step": step,
        "thought": thought,
        "action": action,
        "details": details or {}
    }
