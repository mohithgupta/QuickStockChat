#!/bin/bash

###############################################################################
# Manual Security Verification Script
#
# This script performs comprehensive security verification of the API security
# features implemented in the stockQuickChat application.
#
# Usage:
#   ./scripts/manual_security_verification.sh
#
# Prerequisites:
#   - Backend server running on http://localhost:8000
#   - jq installed (for JSON parsing)
#   - curl installed
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:8000"
API_KEY="${API_KEY:-test-api-key-12345}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}Testing:${NC} $1"
    ((TOTAL_TESTS++))
}

print_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1\n"
    ((PASSED_TESTS++))
}

print_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1\n"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "${BLUE}ℹ INFO:${NC} $1\n"
}

# Check if server is running
check_server() {
    print_header "Checking Server Availability"

    if curl -s -f "${API_BASE_URL}/health" > /dev/null 2>&1; then
        print_pass "Server is running at ${API_BASE_URL}"
        return 0
    else
        print_fail "Server is not accessible at ${API_BASE_URL}"
        print_info "Please start the server with: python main.py"
        exit 1
    fi
}

###############################################################################
# Test 1: Rate Limiting Verification
###############################################################################
test_rate_limiting() {
    print_header "Test 1: Rate Limiting Verification"

    print_test "Sending 101 requests rapidly to test rate limiting (100 req/min limit)"

    # Send 101 requests and count 429 responses
    four_two_nine_count=0
    success_count=0

    for i in {1..101}; do
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE_URL}/health" || echo "000")

        if [ "$status_code" = "429" ]; then
            ((four_two_nine_count++))
        elif [ "$status_code" = "200" ]; then
            ((success_count++))
        fi

        # Small delay to avoid overwhelming the system
        sleep 0.01
    done

    echo "Successful requests: $success_count"
    echo "Rate limited requests (429): $four_two_nine_count"

    if [ $four_two_nine_count -ge 1 ]; then
        print_pass "Rate limiting is working (429 responses received: $four_two_nine_count)"
    else
        print_fail "Rate limiting may not be working (no 429 responses received)"
    fi

    # Test Retry-After header
    print_test "Checking Retry-After header on 429 response"

    # Get a 429 response by making rapid requests
    for i in {1..105}; do
        response=$(curl -s -i "${API_BASE_URL}/health" 2>&1 | head -20)
        retry_after=$(echo "$response" | grep -i "Retry-After:" || echo "")

        if [ -n "$retry_after" ]; then
            print_pass "Retry-After header present: $retry_after"
            break
        fi

        sleep 0.01
    done

    # Wait for rate limit to reset
    print_info "Waiting 60 seconds for rate limit to reset..."
    sleep 60
}

###############################################################################
# Test 2: CORS Verification
###############################################################################
test_cors() {
    print_header "Test 2: CORS Verification"

    # Test allowed origin
    print_test "Testing CORS with allowed origin (http://localhost:5173)"

    cors_response=$(curl -s -i \
        -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: POST" \
        -X OPTIONS "${API_BASE_URL}/api/chat" 2>&1)

    allowed_origin=$(echo "$cors_response" | grep -i "Access-Control-Allow-Origin:" || echo "")

    if echo "$allowed_origin" | grep -q "http://localhost:5173"; then
        print_pass "CORS allows http://localhost:5173"
    else
        print_fail "CORS does not allow http://localhost:5173"
    fi

    # Test unauthorized origin
    print_test "Testing CORS blocks unauthorized origin (http://evil.com)"

    evil_response=$(curl -s -i \
        -H "Origin: http://evil.com" \
        -H "Access-Control-Request-Method: POST" \
        -X OPTIONS "${API_BASE_URL}/api/chat" 2>&1)

    evil_origin=$(echo "$evil_response" | grep -i "Access-Control-Allow-Origin:" || echo "")

    if echo "$evil_origin" | grep -q "http://evil.com"; then
        print_fail "CORS incorrectly allows http://evil.com (should be blocked)"
    else
        print_pass "CORS correctly blocks http://evil.com"
    fi

    # Test preflight OPTIONS method
    print_test "Testing CORS preflight OPTIONS request"

    preflight_response=$(curl -s -i \
        -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS "${API_BASE_URL}/api/chat" 2>&1)

    allowed_methods=$(echo "$preflight_response" | grep -i "Access-Control-Allow-Methods:" || echo "")

    if [ -n "$allowed_methods" ]; then
        print_pass "CORS preflight OPTIONS request successful"
    else
        print_fail "CORS preflight OPTIONS request failed"
    fi
}

###############################################################################
# Test 3: API Key Authentication
###############################################################################
test_authentication() {
    print_header "Test 3: API Key Authentication"

    # Check if auth is enabled
    print_test "Checking if authentication is enabled (REQUIRE_API_KEY=true)"

    auth_test_response=$(curl -s -i \
        -H "Content-Type: application/json" \
        -d '{"prompt":{"content":"test","id":"1","role":"user"},"threadId":"1","responseId":"1"}' \
        "${API_BASE_URL}/api/chat" 2>&1)

    auth_status_code=$(echo "$auth_test_response" | grep "HTTP/" | awk '{print $2}')

    if [ "$auth_status_code" = "401" ] || [ "$auth_status_code" = "403" ]; then
        print_pass "Authentication is enabled (endpoint returns 401/403 without key)"

        # Test valid API key via header
        print_test "Testing valid API key via X-API-Key header"

        auth_header_response=$(curl -s -i \
            -H "Content-Type: application/json" \
            -H "X-API-Key: ${API_KEY}" \
            -d '{"prompt":{"content":"test","id":"1","role":"user"},"threadId":"1","responseId":"1"}' \
            "${API_BASE_URL}/api/chat" 2>&1)

        auth_header_status=$(echo "$auth_header_response" | grep "HTTP/" | awk '{print $2}')

        if [ "$auth_header_status" != "401" ] && [ "$auth_header_status" != "403" ]; then
            print_pass "Valid API key accepted via X-API-Key header (status: $auth_header_status)"
        else
            print_fail "Valid API key rejected via X-API-Key header"
        fi

        # Test valid API key via query parameter
        print_test "Testing valid API key via api_key query parameter"

        auth_query_response=$(curl -s -i \
            -H "Content-Type: application/json" \
            -d '{"prompt":{"content":"test","id":"1","role":"user"},"threadId":"1","responseId":"1"}' \
            "${API_BASE_URL}/api/chat?api_key=${API_KEY}" 2>&1)

        auth_query_status=$(echo "$auth_query_response" | grep "HTTP/" | awk '{print $2}')

        if [ "$auth_query_status" != "401" ] && [ "$auth_query_status" != "403" ]; then
            print_pass "Valid API key accepted via query parameter (status: $auth_query_status)"
        else
            print_fail "Valid API key rejected via query parameter"
        fi

        # Test invalid API key
        print_test "Testing invalid API key (should return 403)"

        invalid_response=$(curl -s -i \
            -H "Content-Type: application/json" \
            -H "X-API-Key: invalid-key-12345" \
            -d '{"prompt":{"content":"test","id":"1","role":"user"},"threadId":"1","responseId":"1"}' \
            "${API_BASE_URL}/api/chat" 2>&1)

        invalid_status=$(echo "$invalid_response" | grep "HTTP/" | awk '{print $2}')

        if [ "$invalid_status" = "403" ]; then
            print_pass "Invalid API key correctly rejected with 403"
        else
            print_fail "Invalid API key not rejected (status: $invalid_status)"
        fi

        # Test missing API key
        print_test "Testing missing API key (should return 401)"

        missing_response=$(curl -s -i \
            -H "Content-Type: application/json" \
            -d '{"prompt":{"content":"test","id":"1","role":"user"},"threadId":"1","responseId":"1"}' \
            "${API_BASE_URL}/api/chat" 2>&1)

        missing_status=$(echo "$missing_response" | grep "HTTP/" | awk '{print $2}')

        if [ "$missing_status" = "401" ]; then
            print_pass "Missing API key correctly rejected with 401"
        else
            print_fail "Missing API key not rejected (status: $missing_status)"
        fi
    else
        print_info "Authentication is not enabled (REQUIRE_API_KEY=false or not set)"
        print_info "Skipping authentication tests"
        print_info "To enable authentication, set REQUIRE_API_KEY=true and API_KEY environment variables"
    fi

    # Test health check endpoint (should never require auth)
    print_test "Testing health check endpoint (should always work without auth)"

    health_response=$(curl -s -i "${API_BASE_URL}/health" 2>&1)
    health_status=$(echo "$health_response" | grep "HTTP/" | awk '{print $2}')

    if [ "$health_status" = "200" ]; then
        print_pass "Health check endpoint works without authentication"
    else
        print_fail "Health check endpoint requires authentication (should not)"
    fi
}

###############################################################################
# Test 4: Security Headers Verification
###############################################################################
test_security_headers() {
    print_header "Test 4: Security Headers Verification"

    # Get headers from health endpoint
    headers_response=$(curl -s -i "${API_BASE_URL}/health" 2>&1)

    # Test X-Content-Type-Options
    print_test "Checking X-Content-Type-Options header"

    content_type_options=$(echo "$headers_response" | grep -i "X-Content-Type-Options:" || echo "")

    if echo "$content_type_options" | grep -iq "nosniff"; then
        print_pass "X-Content-Type-Options: nosniff present"
    else
        print_fail "X-Content-Type-Options header missing or incorrect"
    fi

    # Test X-Frame-Options
    print_test "Checking X-Frame-Options header"

    frame_options=$(echo "$headers_response" | grep -i "X-Frame-Options:" || echo "")

    if echo "$frame_options" | grep -iq "DENY"; then
        print_pass "X-Frame-Options: DENY present"
    else
        print_fail "X-Frame-Options header missing or incorrect"
    fi

    # Test X-XSS-Protection
    print_test "Checking X-XSS-Protection header"

    xss_protection=$(echo "$headers_response" | grep -i "X-XSS-Protection:" || echo "")

    if echo "$xss_protection" | grep -iq "1; mode=block"; then
        print_pass "X-XSS-Protection: 1; mode=block present"
    else
        print_fail "X-XSS-Protection header missing or incorrect"
    fi

    # Test Content-Security-Policy
    print_test "Checking Content-Security-Policy header"

    csp=$(echo "$headers_response" | grep -i "Content-Security-Policy:" || echo "")

    if [ -n "$csp" ]; then
        print_pass "Content-Security-Policy present"

        # Check for specific CSP directives
        if echo "$csp" | grep -iq "default-src 'self'"; then
            print_pass "  - default-src 'self' directive present"
        fi

        if echo "$csp" | grep -iq "frame-ancestors 'none'"; then
            print_pass "  - frame-ancestors 'none' directive present"
        fi
    else
        print_fail "Content-Security-Policy header missing"
    fi

    # Test Strict-Transport-Security (only if HTTPS)
    print_test "Checking Strict-Transport-Security header (HTTPS only)"

    hsts=$(echo "$headers_response" | grep -i "Strict-Transport-Security:" || echo "")

    if [ -n "$hsts" ]; then
        print_pass "Strict-Transport-Security present (HTTPS connection detected)"
    else
        print_info "Strict-Transport-Security not present (HTTP connection - expected for development)"
    fi

    # Test Referrer-Policy
    print_test "Checking Referrer-Policy header"

    referrer_policy=$(echo "$headers_response" | grep -i "Referrer-Policy:" || echo "")

    if echo "$referrer_policy" | grep -iq "strict-origin-when-cross-origin"; then
        print_pass "Referrer-Policy: strict-origin-when-cross-origin present"
    else
        print_fail "Referrer-Policy header missing or incorrect"
    fi

    # Test Permissions-Policy
    print_test "Checking Permissions-Policy header"

    permissions_policy=$(echo "$headers_response" | grep -i "Permissions-Policy:" || echo "")

    if [ -n "$permissions_policy" ]; then
        print_pass "Permissions-Policy present"

        # Check for specific restrictions
        if echo "$permissions_policy" | grep -iq "geology=()"; then
            print_pass "  - Geolocation restricted"
        fi

        if echo "$permissions_policy" | grep -iq "microphone=()"; then
            print_pass "  - Microphone restricted"
        fi

        if echo "$permissions_policy" | grep -iq "camera=()"; then
            print_pass "  - Camera restricted"
        fi
    else
        print_fail "Permissions-Policy header missing"
    fi
}

###############################################################################
# Test 5: External API Throttling
###############################################################################
test_api_throttling() {
    print_header "Test 5: External API Throttling"

    print_info "Note: This test checks for API throttler integration in the code"
    print_info "Actual throttling behavior would require making real stock data requests"

    # Check if throttler is integrated in tools.py
    print_test "Verifying API throttler integration in tools.py"

    if [ -f "MarketInsight/utils/tools.py" ]; then
        if grep -q "from utils.api_throttler import get_throttler" MarketInsight/utils/tools.py; then
            print_pass "API throttler imported in tools.py"
        else
            print_fail "API throttler not imported in tools.py"
        fi

        if grep -q "with throttler.throttle" MarketInsight/utils/tools.py; then
            print_pass "Throttler context manager used in tools.py"
        else
            print_fail "Throttler context manager not used in tools.py"
        fi

        # Count number of functions using throttler
        throttle_count=$(grep -c "with throttler.throttle(\"yfinance\")" MarketInsight/utils/tools.py || echo "0")

        print_info "Number of yfinance API calls wrapped with throttler: $throttle_count"

        if [ "$throttle_count" -gt 0 ]; then
            print_pass "API throttling is integrated ($throttle_count functions protected)"
        else
            print_fail "No API calls are throttled"
        fi
    else
        print_fail "MarketInsight/utils/tools.py not found"
    fi

    # Check for throttler configuration
    print_test "Verifying API throttler configuration"

    if [ -f "utils/api_throttler.py" ]; then
        if grep -q "yfinance.*2.0" utils/api_throttler.py; then
            print_pass "yfinance rate limit configured (2 req/sec)"
        else
            print_fail "yfinance rate limit not configured"
        fi

        if grep -q "openai.*10.0" utils/api_throttler.py; then
            print_pass "OpenAI rate limit configured (10 req/sec)"
        else
            print_fail "OpenAI rate limit not configured"
        fi
    else
        print_fail "utils/api_throttler.py not found"
    fi

    # Check for logging configuration
    print_test "Verifying throttler logging configuration"

    if [ -f "utils/api_throttler.py" ]; then
        if grep -q "logger" utils/api_throttler.py; then
            print_pass "API throttler includes logging"
        else
            print_fail "API throttler missing logging"
        fi
    fi

    print_info "To test actual throttling behavior:"
    print_info "1. Make multiple rapid stock data requests via /api/chat endpoint"
    print_info "2. Check logs for throttler messages: 'Acquired token for yfinance'"
    print_info "3. Verify throttling messages appear between API calls"
}

###############################################################################
# Main execution
###############################################################################
main() {
    print_header "Manual Security Verification"
    print_info "API Base URL: ${API_BASE_URL}"
    print_info "API Key: ${API_KEY:0:8}..."

    # Check server availability
    check_server

    # Run all tests
    test_rate_limiting
    test_cors
    test_authentication
    test_security_headers
    test_api_throttling

    # Print summary
    print_header "Test Summary"
    echo -e "Total Tests:  $TOTAL_TESTS"
    echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
    echo -e "${RED}Failed:       $FAILED_TESTS${NC}"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}All security verification tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}Some security verification tests failed. Please review the output above.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
