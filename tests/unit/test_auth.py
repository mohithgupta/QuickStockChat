"""
Unit tests for middleware/auth.py authentication functions

Tests cover API key validation, authentication modes, and edge cases.
"""

import pytest
import os
from fastapi import HTTPException, status
from unittest.mock import patch


# Import the authentication function
from middleware.auth import get_api_key


class TestGetAPIKeyAuthenticationDisabled:
    """Test suite for get_api_key when authentication is disabled"""

    @pytest.mark.asyncio
    async def test_auth_disabled_returns_none(self):
        """Test get_api_key returns None when REQUIRE_API_KEY is false"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "false"}):
            result = await get_api_key(x_api_key=None, api_key=None)
            assert result is None

    @pytest.mark.asyncio
    async def test_auth_disabled_with_invalid_key_still_returns_none(self):
        """Test get_api_key returns None when auth is disabled, even if key provided"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "false"}):
            # Even with a key, if auth is disabled, it should return None
            result = await get_api_key(x_api_key="some-key", api_key=None)
            assert result is None

    @pytest.mark.asyncio
    async def test_auth_disabled_case_insensitive(self):
        """Test REQUIRE_API_KEY is case-insensitive"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "False"}):
            result = await get_api_key(x_api_key=None, api_key=None)
            assert result is None

        with patch.dict(os.environ, {"REQUIRE_API_KEY": "FALSE"}):
            result = await get_api_key(x_api_key=None, api_key=None)
            assert result is None

    @pytest.mark.asyncio
    async def test_auth_disabled_with_query_param(self):
        """Test get_api_key returns None with query param when auth disabled"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "false"}):
            result = await get_api_key(x_api_key=None, api_key="query-key")
            assert result is None

    @pytest.mark.asyncio
    async def test_auth_disabled_env_var_not_set(self):
        """Test get_api_key returns None when REQUIRE_API_KEY is not set"""
        # Remove REQUIRE_API_KEY from environment
        env_copy = os.environ.copy()
        env_copy.pop("REQUIRE_API_KEY", None)

        with patch.dict(os.environ, env_copy, clear=True):
            result = await get_api_key(x_api_key=None, api_key=None)
            assert result is None


class TestGetAPIKeyAuthenticationEnabled:
    """Test suite for get_api_key when authentication is enabled"""

    @pytest.mark.asyncio
    async def test_auth_enabled_with_valid_header_key(self):
        """Test get_api_key validates key from X-API-Key header"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "test-valid-api-key"
        }):
            result = await get_api_key(x_api_key="test-valid-api-key", api_key=None)
            assert result == "test-valid-api-key"

    @pytest.mark.asyncio
    async def test_auth_enabled_with_valid_query_param_key(self):
        """Test get_api_key validates key from api_key query parameter"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "test-valid-api-key"
        }):
            result = await get_api_key(x_api_key=None, api_key="test-valid-api-key")
            assert result == "test-valid-api-key"

    @pytest.mark.asyncio
    async def test_auth_enabled_header_takes_precedence(self):
        """Test X-API-Key header takes precedence over query parameter"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "test-valid-api-key"
        }):
            # Both provided, header should be used
            result = await get_api_key(
                x_api_key="header-key",
                api_key="query-key"
            )
            assert result == "header-key"

    @pytest.mark.asyncio
    async def test_auth_enabled_with_different_valid_key(self):
        """Test get_api_key works with different valid key"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "super-secret-key-12345"
        }):
            result = await get_api_key(x_api_key="super-secret-key-12345", api_key=None)
            assert result == "super-secret-key-12345"


class TestGetAPIKeyMissingKeyErrors:
    """Test suite for get_apikey error handling when key is missing"""

    @pytest.mark.asyncio
    async def test_auth_enabled_no_key_provided(self):
        """Test get_api_key raises 401 when no key is provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "expected-key"
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key=None, api_key=None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "API key is required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_enabled_empty_string_key(self):
        """Test get_api_key raises 401 when empty string key is provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "expected-key"
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="", api_key=None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_auth_enabled_missing_header_key_with_query_param(self):
        """Test get_api_key uses query param when header is missing"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "expected-key"
        }):
            # Header is None, but query param has key
            result = await get_api_key(x_api_key=None, api_key="expected-key")
            assert result == "expected-key"


class TestGetAPIKeyInvalidKeyErrors:
    """Test suite for get_api_key error handling when key is invalid"""

    @pytest.mark.asyncio
    async def test_auth_enabled_wrong_header_key(self):
        """Test get_api_key raises 403 when header key is wrong"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="wrong-key", api_key=None)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Invalid API key" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_enabled_wrong_query_param_key(self):
        """Test get_api_key raises 403 when query param key is wrong"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key=None, api_key="wrong-key")

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Invalid API key" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_enabled_case_sensitive_key(self):
        """Test get_api_key is case-sensitive"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "SecretKey"
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="secretkey", api_key=None)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_auth_enabled_whitespace_matters(self):
        """Test get_api_key treats whitespace as significant"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "my-key"
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key=" my-key ", api_key=None)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestGetAPIKeyConfigurationErrors:
    """Test suite for get_api_key server configuration error handling"""

    @pytest.mark.asyncio
    async def test_auth_enabled_api_key_env_not_set(self):
        """Test get_api_key raises 500 when API_KEY env var is not set"""
        # Set REQUIRE_API_KEY but not API_KEY
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "true"}, clear=True):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="some-key", api_key=None)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Server configuration error" in exc_info.value.detail
            assert "API key not configured" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_enabled_empty_api_key_env(self):
        """Test get_api_key raises 500 when API_KEY env var is empty"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": ""
        }):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="some-key", api_key=None)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_auth_enabled_no_provided_key_no_env_key(self):
        """Test get_api_key raises 500 when both keys are missing"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true"
        }, clear=True):
            # No API_KEY in env, no key provided
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key=None, api_key=None)

            # Should raise 500 for configuration error, not 401
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestGetAPIKeySpecialCharacters:
    """Test suite for get_api_key with special characters in keys"""

    @pytest.mark.asyncio
    async def test_key_with_special_characters(self):
        """Test get_api_key works with special characters in key"""
        special_key = "key-with-special.chars_123"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": special_key
        }):
            result = await get_api_key(x_api_key=special_key, api_key=None)
            assert result == special_key

    @pytest.mark.asyncio
    async def test_key_with_dashes(self):
        """Test get_api_key works with dashes in key"""
        key = "my-api-key-2024"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": key
        }):
            result = await get_api_key(x_api_key=key, api_key=None)
            assert result == key

    @pytest.mark.asyncio
    async def test_key_with_underscores(self):
        """Test get_api_key works with underscores in key"""
        key = "my_api_key_2024"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": key
        }):
            result = await get_api_key(x_api_key=key, api_key=None)
            assert result == key

    @pytest.mark.asyncio
    async def test_key_with_uuid_format(self):
        """Test get_api_key works with UUID-like key"""
        key = "550e8400-e29b-41d4-a716-446655440000"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": key
        }):
            result = await get_api_key(x_api_key=key, api_key=None)
            assert result == key


class TestGetAPIKeyEdgeCases:
    """Test suite for get_api_key edge cases and unusual scenarios"""

    @pytest.mark.asyncio
    async def test_very_long_key(self):
        """Test get_api_key works with very long keys"""
        long_key = "a" * 1000
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": long_key
        }):
            result = await get_api_key(x_api_key=long_key, api_key=None)
            assert result == long_key

    @pytest.mark.asyncio
    async def test_key_with_unicode_characters(self):
        """Test get_api_key works with unicode characters"""
        unicode_key = "key-with-émojis-🔑"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": unicode_key
        }):
            result = await get_api_key(x_api_key=unicode_key, api_key=None)
            assert result == unicode_key

    @pytest.mark.asyncio
    async def test_both_params_different_values(self):
        """Test get_api_key uses header when both params have different values"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            result = await get_api_key(
                x_api_key="correct-key",
                api_key="wrong-key"
            )
            assert result == "correct-key"

    @pytest.mark.asyncio
    async def test_query_param_fallback(self):
        """Test get_api_key falls back to query param when header is None"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            result = await get_api_key(
                x_api_key=None,
                api_key="correct-key"
            )
            assert result == "correct-key"
