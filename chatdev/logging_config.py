"""Structured logging configuration for ChatDev.

This module provides structured logging using structlog for better
debugging, monitoring, and log analysis.
"""
import logging
import sys
from typing import Any, Dict

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def configure_logging(
    log_level: str = "INFO",
    log_file: str = None,
    json_logs: bool = False
) -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging output
        json_logs: Whether to output logs in JSON format

    Example:
        >>> configure_logging(log_level="DEBUG", json_logs=True)
    """
    if not STRUCTLOG_AVAILABLE:
        # Fallback to standard logging if structlog not available
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='[%(asctime)s %(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> Any:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Structured logger instance or standard logger if structlog unavailable

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("operation_started", phase="coding", agent="programmer")
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


class LogContext:
    """Context manager for adding contextual information to logs.

    Example:
        >>> with LogContext(phase="coding", iteration=1):
        ...     logger.info("processing")
    """

    def __init__(self, **kwargs: Any):
        """Initialize log context.

        Args:
            **kwargs: Context key-value pairs to add to logs
        """
        self.context = kwargs

    def __enter__(self):
        """Enter context and bind context variables."""
        if STRUCTLOG_AVAILABLE:
            structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and unbind context variables."""
        if STRUCTLOG_AVAILABLE:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_function_call(func):
    """Decorator to log function calls with parameters and results.

    Example:
        >>> @log_function_call
        ... def my_function(x: int) -> int:
        ...     return x * 2
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(
            "function_called",
            function=func.__name__,
            args=args,
            kwargs=kwargs
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(
                "function_completed",
                function=func.__name__,
                result=type(result).__name__
            )
            return result
        except Exception as e:
            logger.error(
                "function_failed",
                function=func.__name__,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    return wrapper


# Default logger instance
logger = get_logger("chatdev")


# Convenience functions for common logging patterns
def log_phase_start(phase_name: str, **context: Any) -> None:
    """Log the start of a development phase.

    Args:
        phase_name: Name of the phase starting
        **context: Additional context information
    """
    logger.info(
        "phase_started",
        phase=phase_name,
        event="phase_start",
        **context
    )


def log_phase_end(phase_name: str, duration: float = None, **context: Any) -> None:
    """Log the completion of a development phase.

    Args:
        phase_name: Name of the phase completed
        duration: Phase duration in seconds
        **context: Additional context information
    """
    log_data = {
        "phase": phase_name,
        "event": "phase_end",
        **context
    }
    if duration is not None:
        log_data["duration_seconds"] = duration

    logger.info("phase_completed", **log_data)


def log_api_call(
    api_name: str,
    method: str,
    status: str = "initiated",
    **context: Any
) -> None:
    """Log an API call event.

    Args:
        api_name: Name of the API (e.g., "OpenAI")
        method: API method being called
        status: Call status (initiated, success, failed)
        **context: Additional context (tokens, cost, error, etc.)
    """
    logger.info(
        "api_call",
        api=api_name,
        method=method,
        status=status,
        **context
    )


def log_agent_interaction(
    agent_from: str,
    agent_to: str,
    message_type: str,
    **context: Any
) -> None:
    """Log an interaction between AI agents.

    Args:
        agent_from: Source agent role
        agent_to: Target agent role
        message_type: Type of message/interaction
        **context: Additional context information
    """
    logger.info(
        "agent_interaction",
        from_agent=agent_from,
        to_agent=agent_to,
        message_type=message_type,
        **context
    )


def log_error(
    error_type: str,
    error_message: str,
    **context: Any
) -> None:
    """Log an error with context.

    Args:
        error_type: Type/category of error
        error_message: Error description
        **context: Additional context information
    """
    logger.error(
        "error_occurred",
        error_type=error_type,
        error_message=error_message,
        **context
    )


def log_metric(
    metric_name: str,
    metric_value: float,
    **context: Any
) -> None:
    """Log a metric value.

    Args:
        metric_name: Name of the metric
        metric_value: Metric value
        **context: Additional context (unit, tags, etc.)
    """
    logger.info(
        "metric",
        metric_name=metric_name,
        metric_value=metric_value,
        **context
    )
