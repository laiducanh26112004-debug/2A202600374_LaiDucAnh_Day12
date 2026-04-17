import logging
import time
from functools import wraps
from typing import Callable, Any
from pathlib import Path


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def timer(func: Callable) -> Callable:
    """Decorator to log execution time."""
    logger = setup_logger("timer")

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} completed in {elapsed:.3f}s")
        return result

    return wrapper


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def truncate_text(text: str, max_chars: int) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text