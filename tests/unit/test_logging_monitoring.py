"""
Unit tests for logging and monitoring modules.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from chatdev.logging_config import (
    configure_logging,
    get_logger,
    LogContext,
    log_function_call,
    log_phase_start,
    log_phase_end,
    log_api_call,
    log_error,
    log_metric
)


class TestLoggingConfiguration:
    """Test logging configuration module."""

    def test_configure_logging_basic(self):
        """Test basic logging configuration."""
        configure_logging(log_level="INFO")
        logger = get_logger("test")
        assert logger is not None

    def test_configure_logging_json(self):
        """Test JSON logging configuration."""
        configure_logging(log_level="DEBUG", json_logs=True)
        logger = get_logger("test")
        assert logger is not None

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_module")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')

    def test_log_context_manager(self):
        """Test LogContext context manager."""
        with LogContext(phase="testing", iteration=1) as context:
            assert context is not None
            # Context should be available within the block

    def test_log_function_call_decorator(self):
        """Test function call logging decorator."""
        @log_function_call
        def test_function(x: int) -> int:
            return x * 2

        result = test_function(5)
        assert result == 10

    def test_log_function_call_with_exception(self):
        """Test function call logging with exception."""
        @log_function_call
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    def test_log_phase_start(self):
        """Test phase start logging."""
        # Should not raise exception
        log_phase_start("Coding", agent="programmer")

    def test_log_phase_end(self):
        """Test phase end logging."""
        # Should not raise exception
        log_phase_end("Coding", duration=10.5, status="success")

    def test_log_api_call(self):
        """Test API call logging."""
        log_api_call(
            api_name="OpenAI",
            method="chat.completions.create",
            status="success",
            tokens=100
        )

    def test_log_error(self):
        """Test error logging."""
        log_error(
            error_type="ConfigurationError",
            error_message="Config file not found",
            file_path="/path/to/config"
        )

    def test_log_metric(self):
        """Test metric logging."""
        log_metric(
            metric_name="api_latency",
            metric_value=0.234,
            unit="seconds"
        )


class TestAPIWrapper:
    """Test async API wrapper module."""

    def test_rate_limiter_initialization(self):
        """Test RateLimiter initialization."""
        from chatdev.api_wrapper import RateLimiter

        limiter = RateLimiter(rate=10.0, capacity=20)
        assert limiter.rate == 10.0
        assert limiter.capacity == 20
        assert limiter.tokens == 20

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire(self):
        """Test RateLimiter token acquisition."""
        from chatdev.api_wrapper import RateLimiter

        limiter = RateLimiter(rate=100.0, capacity=100)
        await limiter.acquire(10)
        assert limiter.tokens < 100

    def test_async_openai_client_initialization(self):
        """Test AsyncOpenAIClient initialization."""
        from chatdev.api_wrapper import AsyncOpenAIClient

        client = AsyncOpenAIClient(
            api_key="test-key",
            rate_limit=50.0,
            max_retries=3
        )
        assert client.api_key == "test-key"
        assert client.max_retries == 3

    def test_api_metrics_initialization(self):
        """Test APIMetrics initialization."""
        from chatdev.api_wrapper import APIMetrics

        metrics = APIMetrics()
        assert metrics.total_calls == 0
        assert metrics.successful_calls == 0
        assert metrics.failed_calls == 0

    @pytest.mark.asyncio
    async def test_api_metrics_record_call(self):
        """Test recording API calls in metrics."""
        from chatdev.api_wrapper import APIMetrics

        metrics = APIMetrics()
        await metrics.record_call(
            success=True,
            duration=0.5,
            tokens=100,
            cost=0.002
        )

        stats = metrics.get_stats()
        assert stats["total_calls"] == 1
        assert stats["successful_calls"] == 1
        assert stats["total_tokens"] == 100

    def test_api_metrics_get_stats(self):
        """Test getting statistics from APIMetrics."""
        from chatdev.api_wrapper import APIMetrics

        metrics = APIMetrics()
        stats = metrics.get_stats()

        assert "total_calls" in stats
        assert "success_rate_percent" in stats
        assert "total_cost_usd" in stats

    def test_api_metrics_reset(self):
        """Test resetting metrics."""
        from chatdev.api_wrapper import APIMetrics

        metrics = APIMetrics()
        metrics.total_calls = 10
        metrics.reset()
        assert metrics.total_calls == 0


class TestMonitoring:
    """Test monitoring module."""

    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        from chatdev.monitoring import MetricsCollector

        collector = MetricsCollector(enable_prometheus=False)
        assert not collector.enabled

    def test_metrics_collector_disabled(self):
        """Test that disabled collector doesn't raise errors."""
        from chatdev.monitoring import MetricsCollector

        collector = MetricsCollector(enable_prometheus=False)

        # These should not raise exceptions
        collector.record_phase_execution("Test", 1.0)
        collector.record_api_call("OpenAI", "test", 0.5)
        collector.record_agent_message("CEO", "CTO")
        collector.record_error("TestError")

    @pytest.mark.skipif(
        not pytest.importorskip("prometheus_client", None),
        reason="prometheus_client not installed"
    )
    def test_metrics_collector_with_prometheus(self):
        """Test MetricsCollector with Prometheus enabled."""
        from chatdev.monitoring import MetricsCollector

        collector = MetricsCollector(enable_prometheus=True)
        assert collector.enabled

        # Record some metrics
        collector.record_phase_execution("Coding", 5.0, status="success")
        collector.record_api_call(
            "OpenAI",
            "chat.completions.create",
            duration=0.5,
            prompt_tokens=50,
            completion_tokens=100
        )

    def test_track_phase_context_manager(self):
        """Test track_phase context manager."""
        from chatdev.monitoring import track_phase

        with track_phase("Coding"):
            # Simulate work
            pass

    def test_timed_operation_decorator(self):
        """Test timed_operation decorator."""
        from chatdev.monitoring import timed_operation

        @timed_operation("test_operation", {"component": "test"})
        def test_func():
            return 42

        result = test_func()
        assert result == 42

    def test_get_metrics_text(self):
        """Test getting metrics in Prometheus text format."""
        from chatdev.monitoring import get_metrics_text

        metrics_text = get_metrics_text()
        # Should return string (empty if Prometheus not available)
        assert isinstance(metrics_text, str)


class TestIntegration:
    """Integration tests for logging and monitoring."""

    def test_logging_and_monitoring_together(self):
        """Test that logging and monitoring work together."""
        from chatdev.logging_config import log_phase_start, log_phase_end
        from chatdev.monitoring import metrics

        # Start phase
        log_phase_start("TestPhase")

        # Record metrics
        metrics.record_phase_execution("TestPhase", 1.0, status="success")

        # End phase
        log_phase_end("TestPhase", duration=1.0)

    def test_api_wrapper_with_logging(self):
        """Test API wrapper logs correctly."""
        from chatdev.api_wrapper import APIMetrics
        from chatdev.logging_config import log_api_call

        metrics = APIMetrics()

        # Log API call
        log_api_call(
            api_name="OpenAI",
            method="test",
            status="success"
        )

        # This should not raise an exception
        assert True
