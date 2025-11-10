"""Performance monitoring and metrics collection for ChatDev.

This module provides Prometheus-compatible metrics for monitoring
application performance, API usage, and system health.
"""
import time
from functools import wraps
from typing import Callable, Any, Optional

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary,
        start_http_server, generate_latest, REGISTRY
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from chatdev.logging_config import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and exposes application metrics.

    Provides Prometheus-compatible metrics for monitoring ChatDev performance.
    """

    def __init__(self, enable_prometheus: bool = True):
        """Initialize metrics collector.

        Args:
            enable_prometheus: Whether to enable Prometheus metrics
        """
        self.enabled = enable_prometheus and PROMETHEUS_AVAILABLE

        if not self.enabled:
            if enable_prometheus and not PROMETHEUS_AVAILABLE:
                logger.warning(
                    "Prometheus client not available. Install with: pip install prometheus-client"
                )
            return

        # Phase execution metrics
        self.phase_duration = Histogram(
            'chatdev_phase_duration_seconds',
            'Time spent executing each phase',
            ['phase_name', 'phase_type']
        )

        self.phase_executions = Counter(
            'chatdev_phase_executions_total',
            'Total number of phase executions',
            ['phase_name', 'status']
        )

        # API call metrics
        self.api_calls = Counter(
            'chatdev_api_calls_total',
            'Total number of API calls',
            ['api_name', 'method', 'status']
        )

        self.api_duration = Histogram(
            'chatdev_api_duration_seconds',
            'API call duration',
            ['api_name', 'method']
        )

        self.api_tokens = Counter(
            'chatdev_api_tokens_total',
            'Total API tokens used',
            ['api_name', 'token_type']
        )

        self.api_cost = Counter(
            'chatdev_api_cost_usd',
            'Estimated API cost in USD',
            ['api_name']
        )

        # Agent interaction metrics
        self.agent_messages = Counter(
            'chatdev_agent_messages_total',
            'Total messages exchanged between agents',
            ['from_agent', 'to_agent']
        )

        self.conversation_turns = Histogram(
            'chatdev_conversation_turns',
            'Number of turns in agent conversations',
            ['phase_name']
        )

        # System metrics
        self.active_projects = Gauge(
            'chatdev_active_projects',
            'Number of currently active projects'
        )

        self.software_generated = Counter(
            'chatdev_software_generated_total',
            'Total number of software projects generated',
            ['status']
        )

        # Error metrics
        self.errors = Counter(
            'chatdev_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )

        # Performance metrics
        self.memory_usage = Gauge(
            'chatdev_memory_usage_bytes',
            'Current memory usage in bytes'
        )

        self.cpu_usage = Gauge(
            'chatdev_cpu_usage_percent',
            'Current CPU usage percentage'
        )

    def record_phase_execution(
        self,
        phase_name: str,
        duration: float,
        phase_type: str = "SimplePhase",
        status: str = "success"
    ) -> None:
        """Record phase execution metrics.

        Args:
            phase_name: Name of the executed phase
            duration: Execution duration in seconds
            phase_type: Type of phase (SimplePhase, ComposedPhase)
            status: Execution status (success, failed)
        """
        if not self.enabled:
            return

        self.phase_duration.labels(
            phase_name=phase_name,
            phase_type=phase_type
        ).observe(duration)

        self.phase_executions.labels(
            phase_name=phase_name,
            status=status
        ).inc()

    def record_api_call(
        self,
        api_name: str,
        method: str,
        duration: float,
        status: str = "success",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0
    ) -> None:
        """Record API call metrics.

        Args:
            api_name: Name of the API (e.g., "OpenAI")
            method: API method called
            duration: Call duration in seconds
            status: Call status (success, failed, timeout)
            prompt_tokens: Number of prompt tokens used
            completion_tokens: Number of completion tokens used
            cost: Estimated cost in USD
        """
        if not self.enabled:
            return

        self.api_calls.labels(
            api_name=api_name,
            method=method,
            status=status
        ).inc()

        self.api_duration.labels(
            api_name=api_name,
            method=method
        ).observe(duration)

        if prompt_tokens > 0:
            self.api_tokens.labels(
                api_name=api_name,
                token_type="prompt"
            ).inc(prompt_tokens)

        if completion_tokens > 0:
            self.api_tokens.labels(
                api_name=api_name,
                token_type="completion"
            ).inc(completion_tokens)

        if cost > 0:
            self.api_cost.labels(api_name=api_name).inc(cost)

    def record_agent_message(
        self,
        from_agent: str,
        to_agent: str
    ) -> None:
        """Record agent-to-agent message.

        Args:
            from_agent: Source agent role
            to_agent: Target agent role
        """
        if not self.enabled:
            return

        self.agent_messages.labels(
            from_agent=from_agent,
            to_agent=to_agent
        ).inc()

    def record_conversation(
        self,
        phase_name: str,
        turn_count: int
    ) -> None:
        """Record conversation turn count.

        Args:
            phase_name: Name of the phase
            turn_count: Number of conversation turns
        """
        if not self.enabled:
            return

        self.conversation_turns.labels(
            phase_name=phase_name
        ).observe(turn_count)

    def record_error(
        self,
        error_type: str,
        component: str = "unknown"
    ) -> None:
        """Record an error occurrence.

        Args:
            error_type: Type of error (e.g., "ConfigurationError")
            component: Component where error occurred
        """
        if not self.enabled:
            return

        self.errors.labels(
            error_type=error_type,
            component=component
        ).inc()

    def set_active_projects(self, count: int) -> None:
        """Set current number of active projects.

        Args:
            count: Number of active projects
        """
        if not self.enabled:
            return

        self.active_projects.set(count)

    def record_software_generated(self, status: str = "success") -> None:
        """Record a generated software project.

        Args:
            status: Generation status (success, failed)
        """
        if not self.enabled:
            return

        self.software_generated.labels(status=status).inc()

    def update_system_metrics(self) -> None:
        """Update system resource usage metrics."""
        if not self.enabled:
            return

        try:
            import psutil
            process = psutil.Process()
            self.memory_usage.set(process.memory_info().rss)
            self.cpu_usage.set(process.cpu_percent())
        except ImportError:
            pass  # psutil not available

    def start_http_server(self, port: int = 8000) -> None:
        """Start Prometheus metrics HTTP server.

        Args:
            port: Port to listen on

        Raises:
            RuntimeError: If Prometheus client not available
        """
        if not self.enabled:
            raise RuntimeError("Prometheus metrics not enabled")

        logger.info(f"Starting Prometheus metrics server on port {port}")
        start_http_server(port)


def timed_operation(metric_name: str, labels: dict = None):
    """Decorator to time operations and record metrics.

    Args:
        metric_name: Name of the metric
        labels: Optional labels for the metric

    Example:
        >>> @timed_operation("phase_execution", {"phase": "coding"})
        ... def execute_phase():
        ...     pass
    """
    labels = labels or {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record success
                if PROMETHEUS_AVAILABLE and metrics.enabled:
                    metrics.phase_duration.labels(**labels).observe(duration)

                return result
            except Exception as e:
                duration = time.time() - start_time

                # Record failure
                if PROMETHEUS_AVAILABLE and metrics.enabled:
                    metrics.errors.labels(
                        error_type=type(e).__name__,
                        component=func.__name__
                    ).inc()

                raise

        return wrapper

    return decorator


# Global metrics instance
metrics = MetricsCollector()


# Utility functions for common patterns
def track_phase(phase_name: str, phase_type: str = "SimplePhase"):
    """Context manager to track phase execution.

    Args:
        phase_name: Name of the phase
        phase_type: Type of phase

    Example:
        >>> with track_phase("Coding"):
        ...     execute_coding_phase()
    """
    class PhaseTracker:
        def __init__(self):
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            status = "success" if exc_type is None else "failed"
            metrics.record_phase_execution(
                phase_name=phase_name,
                duration=duration,
                phase_type=phase_type,
                status=status
            )

    return PhaseTracker()


def get_metrics_text() -> str:
    """Get current metrics in Prometheus text format.

    Returns:
        Metrics text or empty string if Prometheus not available
    """
    if not PROMETHEUS_AVAILABLE:
        return ""

    return generate_latest(REGISTRY).decode('utf-8')
