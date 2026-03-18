#!/usr/bin/env python3
"""
Error Handling and Retry Logic for Agent SDK Orchestrator
=========================================================
Comprehensive error handling with exponential backoff retry.
"""

import asyncio
import random
from typing import TypeVar, Callable, Optional, Type
from functools import wraps
from datetime import datetime

from anthropic import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)

from config import get_config
from logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class OrchestratorError(Exception):
    """Base exception for orchestrator errors"""
    pass


class AgentExecutionError(OrchestratorError):
    """Error during agent execution"""
    pass


class AgentTimeoutError(OrchestratorError):
    """Agent execution timeout"""
    pass


class AgentConfigurationError(OrchestratorError):
    """Invalid agent configuration"""
    pass


class QualityGateFailure(OrchestratorError):
    """Quality gate check failed"""
    pass


# Retryable exceptions
RETRYABLE_EXCEPTIONS = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)


def calculate_backoff(
    attempt: int,
    base: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (0-indexed)
        base: Backoff base multiplier
        max_delay: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd

    Returns:
        Delay in seconds
    """
    delay = min(base ** attempt, max_delay)

    if jitter:
        delay = delay * (0.5 + random.random())

    return delay


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_attempts: Optional[int] = None,
    backoff_base: Optional[float] = None,
    backoff_max: Optional[float] = None,
    retryable_exceptions: tuple = RETRYABLE_EXCEPTIONS,
    **kwargs
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_attempts: Maximum retry attempts (from config if None)
        backoff_base: Backoff base multiplier (from config if None)
        backoff_max: Maximum backoff delay (from config if None)
        retryable_exceptions: Tuple of exceptions to retry on
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        Last exception if all retries exhausted
    """
    config = get_config()

    max_attempts = max_attempts or config.execution.retry_attempts
    backoff_base = backoff_base or config.execution.retry_backoff_base
    backoff_max = backoff_max or config.execution.retry_backoff_max

    last_exception = None

    for attempt in range(max_attempts):
        try:
            logger.debug(
                "Attempting function call",
                function=func.__name__,
                attempt=attempt + 1,
                max_attempts=max_attempts
            )

            result = await func(*args, **kwargs)

            if attempt > 0:
                logger.info(
                    "Function succeeded after retries",
                    function=func.__name__,
                    attempts=attempt + 1
                )

            return result

        except retryable_exceptions as e:
            last_exception = e

            if attempt < max_attempts - 1:
                delay = calculate_backoff(attempt, backoff_base, backoff_max)

                logger.warning(
                    "Retryable error occurred, backing off",
                    function=func.__name__,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    error=str(e),
                    error_type=type(e).__name__,
                    backoff_seconds=delay
                )

                await asyncio.sleep(delay)
            else:
                logger.error(
                    "All retry attempts exhausted",
                    function=func.__name__,
                    attempts=max_attempts,
                    error=str(e),
                    error_type=type(e).__name__
                )

        except Exception as e:
            # Non-retryable exception
            logger.error(
                "Non-retryable error occurred",
                function=func.__name__,
                attempt=attempt + 1,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    # All retries exhausted
    raise last_exception


def with_retry(
    max_attempts: Optional[int] = None,
    backoff_base: Optional[float] = None,
    backoff_max: Optional[float] = None,
    retryable_exceptions: tuple = RETRYABLE_EXCEPTIONS,
):
    """
    Decorator to add retry logic to async functions.

    Args:
        max_attempts: Maximum retry attempts
        backoff_base: Backoff base multiplier
        backoff_max: Maximum backoff delay
        retryable_exceptions: Tuple of exceptions to retry on

    Example:
        @with_retry(max_attempts=5)
        async def call_api():
            return await client.call()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                *args,
                max_attempts=max_attempts,
                backoff_base=backoff_base,
                backoff_max=backoff_max,
                retryable_exceptions=retryable_exceptions,
                **kwargs
            )
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling and reporting"""

    def __init__(self):
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def record_error(
        self,
        error: Exception,
        context: Optional[dict] = None,
        severity: str = "error"
    ) -> None:
        """Record an error with context"""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity,
            "context": context or {}
        }

        if severity == "warning":
            self.warnings.append(error_record)
            logger.warning(
                "Warning recorded",
                **error_record
            )
        else:
            self.errors.append(error_record)
            logger.error(
                "Error recorded",
                **error_record
            )

    def has_errors(self) -> bool:
        """Check if any errors were recorded"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if any warnings were recorded"""
        return len(self.warnings) > 0

    def get_summary(self) -> dict:
        """Get error summary"""
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }

    def clear(self) -> None:
        """Clear recorded errors and warnings"""
        self.errors.clear()
        self.warnings.clear()


# Global error handler instance
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return _error_handler
