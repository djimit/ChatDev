"""Async API wrapper with rate limiting and retry logic for ChatDev.

This module provides asynchronous API calls with built-in rate limiting,
retry mechanisms, and better error handling.
"""
import asyncio
import time
from typing import Dict, Any, Optional
from functools import wraps

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from chatdev.exceptions import APIError
from chatdev.logging_config import get_logger, log_api_call

logger = get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls.

    Implements a token bucket algorithm to limit API request rate.
    """

    def __init__(self, rate: float, capacity: int):
        """Initialize rate limiter.

        Args:
            rate: Tokens per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens from the bucket, waiting if necessary.

        Args:
            tokens: Number of tokens to acquire

        Raises:
            ValueError: If requested tokens exceed capacity
        """
        if tokens > self.capacity:
            raise ValueError(f"Requested {tokens} tokens exceeds capacity {self.capacity}")

        async with self.lock:
            while self.tokens < tokens:
                now = time.time()
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens < tokens:
                    sleep_time = (tokens - self.tokens) / self.rate
                    await asyncio.sleep(sleep_time)

            self.tokens -= tokens
            self.last_update = time.time()


class AsyncOpenAIClient:
    """Async wrapper for OpenAI API with rate limiting and retries.

    Provides async methods for calling OpenAI API with automatic rate
    limiting, retry logic, and error handling.
    """

    def __init__(
        self,
        api_key: str,
        rate_limit: float = 50.0,  # requests per second
        max_retries: int = 3,
        timeout: int = 300
    ):
        """Initialize async OpenAI client.

        Args:
            api_key: OpenAI API key
            rate_limit: Maximum requests per second
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.rate_limiter = RateLimiter(rate=rate_limit, capacity=int(rate_limit * 2))
        self.max_retries = max_retries
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Enter async context and create session."""
        if AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context and close session."""
        if self.session:
            await self.session.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        before_sleep=before_sleep_log(logger, "WARNING")
    )
    async def create_chat_completion(
        self,
        model: str,
        messages: list,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Create a chat completion with retry and rate limiting.

        Args:
            model: Model name (e.g., "gpt-3.5-turbo", "gpt-4")
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API

        Returns:
            API response dictionary

        Raises:
            APIError: If API call fails after retries
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for async API calls")

        await self.rate_limiter.acquire()

        log_api_call(
            api_name="OpenAI",
            method="chat.completions.create",
            model=model,
            message_count=len(messages)
        )

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        start_time = time.time()

        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                duration = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    log_api_call(
                        api_name="OpenAI",
                        method="chat.completions.create",
                        status="success",
                        duration=duration,
                        prompt_tokens=data.get("usage", {}).get("prompt_tokens"),
                        completion_tokens=data.get("usage", {}).get("completion_tokens")
                    )
                    return data
                else:
                    error_text = await response.text()
                    log_api_call(
                        api_name="OpenAI",
                        method="chat.completions.create",
                        status="failed",
                        status_code=response.status,
                        error=error_text
                    )
                    raise APIError(
                        f"OpenAI API request failed",
                        api_name="OpenAI",
                        status_code=response.status
                    )

        except asyncio.TimeoutError as e:
            duration = time.time() - start_time
            log_api_call(
                api_name="OpenAI",
                method="chat.completions.create",
                status="timeout",
                duration=duration
            )
            raise APIError(
                "OpenAI API request timed out",
                api_name="OpenAI",
                retry_count=self.max_retries
            ) from e

        except Exception as e:
            duration = time.time() - start_time
            log_api_call(
                api_name="OpenAI",
                method="chat.completions.create",
                status="error",
                duration=duration,
                error=str(e)
            )
            raise APIError(
                f"OpenAI API request failed: {str(e)}",
                api_name="OpenAI"
            ) from e


def with_retry(max_attempts: int = 3):
    """Decorator to add retry logic to functions.

    Args:
        max_attempts: Maximum number of retry attempts

    Example:
        >>> @with_retry(max_attempts=3)
        ... def unstable_operation():
        ...     # operation that might fail
        ...     pass
    """
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            before_sleep=before_sleep_log(logger, "WARNING")
        )
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Return appropriate wrapper based on whether func is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            # For sync functions, use tenacity directly
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=1, min=2, max=10)
            )(func)

    return decorator


class APIMetrics:
    """Track API usage metrics.

    Collects statistics about API calls for monitoring and optimization.
    """

    def __init__(self):
        """Initialize metrics tracker."""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_duration = 0.0
        self.lock = asyncio.Lock()

    async def record_call(
        self,
        success: bool,
        duration: float,
        tokens: int = 0,
        cost: float = 0.0
    ) -> None:
        """Record an API call.

        Args:
            success: Whether the call was successful
            duration: Call duration in seconds
            tokens: Number of tokens used
            cost: Estimated cost in USD
        """
        async with self.lock:
            self.total_calls += 1
            if success:
                self.successful_calls += 1
            else:
                self.failed_calls += 1
            self.total_tokens += tokens
            self.total_cost += cost
            self.total_duration += duration

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics.

        Returns:
            Dictionary of statistics
        """
        success_rate = (
            self.successful_calls / self.total_calls * 100
            if self.total_calls > 0
            else 0.0
        )

        avg_duration = (
            self.total_duration / self.total_calls
            if self.total_calls > 0
            else 0.0
        )

        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate_percent": round(success_rate, 2),
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "total_duration_seconds": round(self.total_duration, 2),
            "average_duration_seconds": round(avg_duration, 3)
        }

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_duration = 0.0


# Global metrics instance
api_metrics = APIMetrics()
