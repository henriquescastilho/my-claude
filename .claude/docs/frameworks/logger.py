#!/usr/bin/env python3
"""
Structured Logging for Agent SDK Orchestrator
=============================================
Rich, structured logging with context and observability.
"""

import sys
import logging
import structlog
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler

from config import get_config


# Global console for rich output
console = Console()


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    json_logs: bool = False
) -> None:
    """
    Setup structured logging with rich console output.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        json_logs: Use JSON format for logs
    """
    config = get_config()

    # Use config values if not provided
    level = level or config.logging.level
    log_file = log_file or config.logging.file
    json_logs = config.logging.format == "json"

    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        handlers=[]
    )

    # Add console handler with rich formatting
    if config.logging.console_enabled:
        console_handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            console=console
        )
        logging.root.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.root.addHandler(file_handler)

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding structured logging context"""

    def __init__(self, **kwargs):
        self.context = kwargs

    def __enter__(self):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.clear_contextvars()


# Performance tracking decorator
def log_execution_time(logger: Optional[structlog.BoundLogger] = None):
    """Decorator to log function execution time"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            start_time = datetime.now()
            logger.info(
                f"Starting {func.__name__}",
                function=func.__name__,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )

            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Completed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    success=True
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"Failed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    error=str(e),
                    error_type=type(e).__name__,
                    success=False
                )
                raise

        def sync_wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            start_time = datetime.now()
            logger.info(
                f"Starting {func.__name__}",
                function=func.__name__,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )

            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Completed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    success=True
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"Failed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    error=str(e),
                    error_type=type(e).__name__,
                    success=False
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
