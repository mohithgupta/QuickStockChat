# Test Coverage Summary

**Generated:** 2026-02-03 17:21 +0530
**Total Coverage:** 95% ✓ (Exceeds 80% requirement)

## Coverage Breakdown by Module

| Module | Statements | Missing | Coverage |
|--------|-----------|---------|----------|
| **MarketInsight/components/agent.py** | 12 | 0 | 100% ✓ |
| **MarketInsight/utils/logger.py** | 26 | 0 | 100% ✓ |
| **MarketInsight/utils/tools.py** | 280 | 12 | 96% ✓ |
| **config/config.py** | 9 | 0 | 100% ✓ |
| **main.py** | 38 | 6 | 84% ✓ |
| **TOTAL** | **365** | **18** | **95%** ✓ |

## Coverage Details

### MarketInsight/components/agent.py
- **Coverage:** 100% (12/12 statements)
- **Status:** Fully covered
- **Test Files:**
  - tests/integration/test_agent_workflow.py (18 tests)

### MarketInsight/utils/logger.py
- **Coverage:** 100% (26/26 statements)
- **Status:** Fully covered
- **Test Files:**
  - tests/unit/test_logger.py (37 tests)

### MarketInsight/utils/tools.py
- **Coverage:** 96% (268/280 statements)
- **Status:** Excellent coverage
- **Missing:** 12 statements (mostly edge cases and error paths)
- **Test Files:**
  - tests/unit/test_tools_1_4.py (32 tests)
  - tests/unit/test_tools_5_8.py (37 tests)
  - tests/unit/test_tools_9_12.py (39 tests)
  - tests/unit/test_tools_13_16.py (46 tests)

### config/config.py
- **Coverage:** 100% (9/9 statements)
- **Status:** Fully covered
- **Test Files:**
  - tests/unit/test_config.py (30 tests)

### main.py
- **Coverage:** 84% (32/38 statements)
- **Status:** Good coverage (exceeds 80%)
- **Missing:** 6 statements (mainly error handling and startup edge cases)
- **Test Files:**
  - tests/integration/test_health_endpoint.py (10 tests)
  - tests/integration/test_chat_endpoint.py (23 tests)

## HTML Coverage Report

A detailed HTML coverage report is available in the `htmlcov/` directory:
- **Main Index:** `htmlcov/index.html`
- **Module Details:** Individual HTML files for each module
- **Last Updated:** 2026-02-03 17:21 +0530

## Verification

The coverage report was generated using:
```bash
pytest --cov=. --cov-report=term-missing --cov-report=html tests/
```

## Conclusion

✓ **95% total coverage** significantly exceeds the 80% minimum requirement
✓ All critical business logic is covered by tests
✓ HTML coverage report available for detailed analysis
✓ Coverage threshold enforced in CI/CD pipeline

## Next Steps

1. Review uncovered lines in main.py (6 statements)
2. Consider adding tests for edge cases in tools.py (12 statements)
3. Maintain or improve current coverage levels
4. Monitor coverage in CI/CD pipeline via GitHub Actions
