"""
API Throttler Utility

This module provides a token bucket rate limiter for external API calls to prevent
exceeding rate limits and control costs for services like Yahoo Finance and OpenAI.

Example:
    >>> throttler = APIThrottler()
    >>> with throttler.throttle("yfinance"):
    ...     result = yf.Ticker("AAPL").info
"""

import time
import threading
from typing import Dict, Optional
from MarketInsight.utils.logger import get_logger

logger = get_logger("APIThrottler")


class APIThrottler:
    """
    Token bucket rate limiter for external API calls.

    This class implements a thread-safe token bucket algorithm to throttle
    API calls to external services. Each API provider can have its own
    rate limit configuration.

    Attributes:
        _tokens: Dictionary tracking available tokens per API provider
        _last_update: Dictionary tracking last token refill time per provider
        _lock: Thread lock for thread-safe operations
        _rate_limits: Dictionary of rate limits (requests per second) per provider
    """

    # Default rate limits (requests per second)
    DEFAULT_RATE_LIMITS = {
        "yfinance": 2.0,      # 2 requests/second = 120/minute
        "openai": 10.0,       # 10 requests/second = 600/minute
        "default": 1.0,       # 1 request/second = 60/minute
    }

    # Default bucket capacity (max tokens)
    DEFAULT_CAPACITY = 10

    def __init__(
        self,
        rate_limits: Optional[Dict[str, float]] = None,
        capacity: int = DEFAULT_CAPACITY
    ):
        """
        Initialize the API throttler.

        Args:
            rate_limits: Dictionary of rate limits (requests/second) per provider.
                        If None, uses DEFAULT_RATE_LIMITS.
            capacity: Maximum number of tokens a bucket can hold.
        """
        self._rate_limits = {**self.DEFAULT_RATE_LIMITS, **(rate_limits or {})}
        self._capacity = capacity
        self._tokens: Dict[str, float] = {}
        self._last_update: Dict[str, float] = {}
        self._lock = threading.Lock()

        logger.info(
            f"Initialized APIThrottler with capacity={capacity}, "
            f"rate_limits={self._rate_limits}"
        )

    def _get_rate_limit(self, api_provider: str) -> float:
        """
        Get the rate limit for a specific API provider.

        Args:
            api_provider: Name of the API provider.

        Returns:
            Rate limit in requests per second.
        """
        return self._rate_limits.get(
            api_provider,
            self._rate_limits.get("default", 1.0)
        )

    def _refill_tokens(self, api_provider: str, current_time: float) -> None:
        """
        Refill tokens based on time elapsed since last update.

        Args:
            api_provider: Name of the API provider.
            current_time: Current timestamp in seconds.
        """
        if api_provider not in self._last_update:
            self._tokens[api_provider] = self._capacity
            self._last_update[api_provider] = current_time
            return

        # Calculate time elapsed and tokens to add
        time_elapsed = current_time - self._last_update[api_provider]
        rate_limit = self._get_rate_limit(api_provider)
        tokens_to_add = time_elapsed * rate_limit

        # Refill tokens up to capacity
        current_tokens = self._tokens.get(api_provider, 0.0)
        self._tokens[api_provider] = min(
            self._capacity,
            current_tokens + tokens_to_add
        )
        self._last_update[api_provider] = current_time

    def acquire_token(self, api_provider: str, timeout: Optional[float] = None) -> bool:
        """
        Attempt to acquire a token for an API call.

        If no tokens are available, this method will wait until a token becomes
        available or the timeout is reached.

        Args:
            api_provider: Name of the API provider.
            timeout: Maximum time to wait for a token in seconds.
                    If None, waits indefinitely. Default is None.

        Returns:
            True if a token was acquired, False if timeout was reached.

        Example:
            >>> throttler = APIThrottler()
            >>> if throttler.acquire_token("yfinance", timeout=5.0):
            ...     make_api_call()
        """
        start_time = time.time()
        logger.info(f"Attempting to acquire token for {api_provider}")

        while True:
            with self._lock:
                current_time = time.time()
                self._refill_tokens(api_provider, current_time)

                if self._tokens[api_provider] >= 1.0:
                    self._tokens[api_provider] -= 1.0
                    elapsed = time.time() - start_time
                    logger.info(
                        f"Acquired token for {api_provider} in {elapsed:.3f} seconds. "
                        f"Remaining tokens: {self._tokens[api_provider]:.1f}"
                    )
                    return True

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.warning(
                        f"Failed to acquire token for {api_provider} "
                        f"after {timeout:.3f} seconds timeout"
                    )
                    return False

            # Wait a bit before retrying
            time.sleep(0.01)

    def throttle(self, api_provider: str, timeout: Optional[float] = None):
        """
        Context manager for throttling API calls.

        This is the recommended way to use the throttler. It will automatically
        acquire a token and release it when the context exits.

        Args:
            api_provider: Name of the API provider.
            timeout: Maximum time to wait for a token in seconds.
                    If None, waits indefinitely. Default is None.

        Yields:
            None

        Raises:
            TimeoutError: If timeout is reached before acquiring a token.

        Example:
            >>> throttler = APIThrottler()
            >>> with throttler.throttle("yfinance"):
            ...     result = yf.Ticker("AAPL").info
        """
        class ThrottleContext:
            def __init__(self, throttler_instance: APIThrottler, provider: str, timeout_val: Optional[float]):
                self.throttler = throttler_instance
                self.provider = provider
                self.timeout = timeout_val
                self.acquired = False

            def __enter__(self):
                if not self.throttler.acquire_token(self.provider, self.timeout):
                    raise TimeoutError(
                        f"Could not acquire token for {self.provider} "
                        f"within {self.timeout} seconds"
                    )
                self.acquired = True
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.acquired:
                    logger.debug(f"Releasing context for {self.provider}")
                return False

        return ThrottleContext(self, api_provider, timeout)

    def get_available_tokens(self, api_provider: str) -> float:
        """
        Get the number of available tokens for an API provider.

        Args:
            api_provider: Name of the API provider.

        Returns:
            Number of available tokens.
        """
        with self._lock:
            current_time = time.time()
            self._refill_tokens(api_provider, current_time)
            return self._tokens.get(api_provider, 0.0)

    def reset(self, api_provider: Optional[str] = None) -> None:
        """
        Reset tokens for an API provider or all providers.

        This method is primarily useful for testing.

        Args:
            api_provider: Name of the API provider to reset.
                         If None, resets all providers.
        """
        with self._lock:
            if api_provider:
                self._tokens[api_provider] = self._capacity
                self._last_update[api_provider] = time.time()
                logger.info(f"Reset tokens for {api_provider}")
            else:
                current_time = time.time()
                for provider in self._rate_limits.keys():
                    self._tokens[provider] = self._capacity
                    self._last_update[provider] = current_time
                logger.info("Reset tokens for all providers")


# Create a singleton instance for convenient use
_default_throttler: Optional[APIThrottler] = None


def get_throttler() -> APIThrottler:
    """
    Get the default singleton throttler instance.

    Returns:
        The default APIThrottler instance.
    """
    global _default_throttler
    if _default_throttler is None:
        _default_throttler = APIThrottler()
    return _default_throttler
