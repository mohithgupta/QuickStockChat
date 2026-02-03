# Security Verification Scripts

This directory contains scripts for verifying the security implementation of the stockQuickChat application.

## Available Scripts

### manual_security_verification.sh

Comprehensive automated security verification script that tests all implemented security features.

**Features:**
- ✅ Rate limiting verification (100 req/min limit)
- ✅ CORS policy validation
- ✅ API key authentication testing
- ✅ Security headers verification
- ✅ External API throttling checks

**Usage:**
```bash
# Make sure the backend server is running
python main.py

# In another terminal, run the verification script
./scripts/manual_security_verification.sh
```

**Prerequisites:**
- Backend server running on `http://localhost:8000`
- `curl` installed
- `jq` installed (optional, for JSON parsing)
- Bash shell

**Environment Variables:**
```bash
# Optional: Set API key for authentication tests
export API_KEY=your-test-api-key-12345

# Optional: Override default API URL
export API_BASE_URL=http://localhost:8000
```

**Test Coverage:**
1. **Rate Limiting**
   - Sends 101 rapid requests
   - Verifies 429 responses after limit exceeded
   - Checks Retry-After header

2. **CORS Security**
   - Tests allowed origins (localhost:5173, localhost:3000)
   - Verifies unauthorized origins are blocked (evil.com)
   - Validates preflight OPTIONS requests

3. **API Authentication**
   - Tests valid API keys (header and query parameter)
   - Tests invalid/missing API keys
   - Verifies health check exemption

4. **Security Headers**
   - Verifies X-Content-Type-Options: nosniff
   - Verifies X-Frame-Options: DENY
   - Verifies X-XSS-Protection: 1; mode=block
   - Verifies Content-Security-Policy
   - Verifies Strict-Transport-Security
   - Verifies Referrer-Policy
   - Verifies Permissions-Policy

5. **API Throttling**
   - Verifies throttler integration in code
   - Checks configuration values
   - Validates logging setup

**Output:**
The script provides colored output with pass/fail indicators:
- 🟢 Green: Test passed
- 🔴 Red: Test failed
- 🔵 Blue: Information
- 🟡 Yellow: Test in progress

**Exit Codes:**
- `0`: All tests passed
- `1`: Some tests failed or server not accessible

## Documentation

See [SECURITY_VERIFICATION.md](../SECURITY_VERIFICATION.md) for detailed verification results and security assessment.

## Quick Start

```bash
# 1. Start the backend server
python main.py

# 2. In another terminal, run verification
cd /path/to/stockQuickChat
./scripts/manual_security_verification.sh

# 3. Review the results
# All tests should show green checkmarks
```

## Troubleshooting

**Server not accessible:**
```bash
# Check if server is running
curl http://localhost:8000/health

# Should return: {"status":"ok","message":"Service is running"}
```

**Rate limiting test fails:**
- Wait 60 seconds for rate limit to reset between test runs
- Check if slowapi is installed: `pip list | grep slowapi`

**Authentication tests skipped:**
- Set `REQUIRE_API_KEY=true` in environment or .env file
- Set `API_KEY` environment variable

**Permission denied:**
```bash
# Make script executable
chmod +x scripts/manual_security_verification.sh
```

## Contributing

When adding new security features:
1. Update this README with new test coverage
2. Add tests to manual_security_verification.sh
3. Update SECURITY_VERIFICATION.md with results
4. Ensure all tests pass before committing

## Security Best Practices

1. **Run verification regularly** - Especially after security updates
2. **Test in production-like environment** - Use production CORS origins
3. **Monitor logs** - Check for security events
4. **Keep dependencies updated** - Regular security audits
5. **Review authentication logs** - Monitor for unauthorized access attempts

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
