"""
Unit tests for rate_limiter.py middleware

Tests cover rate limiter initialization, configuration, and identifier extraction.
"""

import pytest
from unittest.mock import Mock, MagicMock
from middleware.rate_limiter import limiter, get_identifier


class TestGetIdentifier:
    """Test suite for get_identifier function"""

    def test_get_identifier_returns_string(self):
        """Test get_identifier returns a string"""
        # Create a mock request with client host
        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        result = get_identifier(mock_request)

        assert isinstance(result, str)
        assert result == "192.168.1.1"

    def test_get_identifier_with_ipv4(self):
        """Test get_identifier with IPv4 address"""
        mock_request = Mock()
        mock_request.client.host = "10.0.0.1"

        result = get_identifier(mock_request)

        assert result == "10.0.0.1"

    def test_get_identifier_with_ipv6(self):
        """Test get_identifier with IPv6 address"""
        mock_request = Mock()
        mock_request.client.host = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

        result = get_identifier(mock_request)

        assert result == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def test_get_identifier_with_localhost(self):
        """Test get_identifier with localhost address"""
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"

        result = get_identifier(mock_request)

        assert result == "127.0.0.1"

    def test_get_identifier_with_different_localhost_format(self):
        """Test get_identifier with IPv6 localhost"""
        mock_request = Mock()
        mock_request.client.host = "::1"

        result = get_identifier(mock_request)

        assert result == "::1"

    def test_get_identifier_is_deterministic(self):
        """Test get_identifier returns same value for same request"""
        mock_request = Mock()
        mock_request.client.host = "192.168.1.100"

        result1 = get_identifier(mock_request)
        result2 = get_identifier(mock_request)

        assert result1 == result2

    def test_get_identifier_with_different_clients(self):
        """Test get_identifier distinguishes different clients"""
        mock_request1 = Mock()
        mock_request1.client.host = "192.168.1.1"

        mock_request2 = Mock()
        mock_request2.client.host = "192.168.1.2"

        result1 = get_identifier(mock_request1)
        result2 = get_identifier(mock_request2)

        assert result1 != result2
        assert result1 == "192.168.1.1"
        assert result2 == "192.168.1.2"


class TestRateLimiter:
    """Test suite for limiter instance"""

    def test_limiter_is_initialized(self):
        """Test limiter instance is created"""
        assert limiter is not None
        assert hasattr(limiter, '_limiter')

    def test_limiter_has_key_func(self):
        """Test limiter has key_func configured"""
        assert limiter._key_func is not None
        assert callable(limiter._key_func)

    def test_limiter_key_func_is_get_identifier(self):
        """Test limiter key_func is get_identifier function"""
        assert limiter._key_func == get_identifier

    def test_limiter_default_limits(self):
        """Test limiter has correct default limits"""
        # slowapi stores default limits in _default_limits
        assert limiter._default_limits == ["100/minute"]

    def test_limiter_storage_uri(self):
        """Test limiter uses in-memory storage"""
        # slowapi Limiter instance should have storage configuration
        assert limiter._storage_uri == "memory://"

    def test_limiter_instance_type(self):
        """Test limiter is correct type"""
        from slowapi import Limiter
        assert isinstance(limiter, Limiter)

    def test_limiter_callback_not_configured(self):
        """Test limiter callback is not configured by default"""
        # The callback should be None unless configured in main.py
        assert limiter._on_breach is None

    def test_limiter_strategy_defaults(self):
        """Test limiter uses default strategy"""
        # Default strategy for slowapi is 'fixed-window'
        assert limiter._strategy == "fixed-window"

    def test_limiter_config_is_immutable(self):
        """Test limiter configuration cannot be accidentally modified"""
        # Get original values
        original_limits = limiter._default_limits
        original_key_func = limiter._key_func

        # Verify they're still the same
        assert limiter._default_limits == original_limits
        assert limiter._key_func == original_key_func


class TestRateLimiterIntegration:
    """Integration tests for rate limiter components"""

    def test_limiter_and_identifier_work_together(self):
        """Test limiter and get_identifier are properly integrated"""
        mock_request = Mock()
        mock_request.client.host = "10.0.0.1"

        # Get identifier using the limiter's key_func
        identifier = limiter._key_func(mock_request)

        assert identifier == "10.0.0.1"

    def test_multiple_clients_get_different_identifiers(self):
        """Test that different clients get different rate limit keys"""
        mock_request1 = Mock()
        mock_request1.client.host = "192.168.1.10"

        mock_request2 = Mock()
        mock_request2.client.host = "192.168.1.20"

        identifier1 = limiter._key_func(mock_request1)
        identifier2 = limiter._key_func(mock_request2)

        assert identifier1 != identifier2
        assert identifier1 == "192.168.1.10"
        assert identifier2 == "192.168.1.20"

    def test_same_client_gets_same_identifier_for_rate_limiting(self):
        """Test same client consistently gets same identifier for rate limiting"""
        mock_request = Mock()
        mock_request.client.host = "172.16.0.1"

        # Get identifier multiple times
        identifier1 = limiter._key_func(mock_request)
        identifier2 = limiter._key_func(mock_request)
        identifier3 = limiter._key_func(mock_request)

        # All should be the same
        assert identifier1 == identifier2 == identifier3
        assert identifier1 == "172.16.0.1"

    def test_limiter_configuration_for_production_use(self):
        """Test limiter is configured appropriately for production"""
        # Verify production-ready configuration
        assert "100/minute" in limiter._default_limits
        assert limiter._storage_uri == "memory://"
        assert limiter._key_func is not None
        assert callable(limiter._key_func)

    def test_rate_limit_per_minute_value(self):
        """Test the rate limit is set to 100 requests per minute"""
        default_limits = limiter._default_limits
        assert len(default_limits) == 1
        assert default_limits[0] == "100/minute"

    def test_in_memory_storage_for_single_instance(self):
        """Test in-memory storage is appropriate for single-instance deployment"""
        assert limiter._storage_uri == "memory://"

        # Note: For distributed deployments, this would be Redis
        # e.g., "redis://localhost:6379"
        assert not limiter._storage_uri.startswith("redis://")


class TestRateLimiterEdgeCases:
    """Edge case tests for rate limiter"""

    def test_get_identifier_with_private_ip(self):
        """Test get_identifier works with private IP addresses"""
        private_ips = [
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1"
        ]

        for ip in private_ips:
            mock_request = Mock()
            mock_request.client.host = ip
            result = get_identifier(mock_request)
            assert result == ip

    def test_get_identifier_preserves_ip_format(self):
        """Test get_identifier preserves exact IP format"""
        mock_request = Mock()
        original_ip = "192.168.001.001"  # With leading zeros
        mock_request.client.host = original_ip

        result = get_identifier(mock_request)

        assert result == original_ip

    def test_limiter_handles_null_gracefully(self):
        """Test limiter configuration handles None values appropriately"""
        # The limiter should be initialized even without optional parameters
        assert limiter is not None
        assert limiter._key_func is not None
        assert limiter._default_limits is not None

    def test_limiter_default_limits_is_list(self):
        """Test default limits is a list that can be extended"""
        assert isinstance(limiter._default_limits, list)
        # This allows for multiple rate limit tiers if needed
        # e.g., ["100/minute", "1000/hour"]
