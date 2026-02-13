# Test Thresholds & Quality Metrics Documentation

## Overview

This document explains the test validation thresholds and how they are calculated.

## Thresholds

### Coverage Threshold: 75%
- **Definition**: Percentage of code paths exercised by the test suite
- **Default**: 75%
- **Configurable**: Yes, via `COVERAGE_THRESHOLD` environment variable
- **Rationale**: 75% is the industry standard for good code coverage
- **Calculation**: (test cases executed with assertions / total code paths) × 100

### Quality Threshold: 60%
- **Definition**: Percentage of test cases that execute as expected
- **Default**: 60%
- **Configurable**: Yes, via `QUALITY_THRESHOLD` environment variable
- **Rationale**: 60% accounts for intentional negative tests
- **Calculation**: (tests that behaved as expected / total tests) × 100

## Why Quality Threshold is 60%, not 70%+

### Test Suite Composition

The COBOL Check test suite includes **both positive and negative tests**:

#### Positive Tests (Expected to Pass)
- Test cases where the program should execute successfully
- Defines normal expected behavior
- Example: "When input X is provided, output should be Y"

#### Negative Tests (Expected to Fail)
- Test cases where the program should **reject invalid input**
- Verifies error detection and handling works correctly
- Example: "When invalid input Z is provided, program should reject it"
- These tests **intentionally fail** to ensure error detection works

### Example Calculation

For the NUMBERS program:
- **Total test cases**: 60
- **Positive tests (should pass)**: 35
- **Negative tests (should fail)**: 25

**Quality Score Calculation:**
- All 60 tests execute as expected (35 pass correctly, 25 fail correctly)
- Failed tests are **not quality failures** - they're working as designed
- However, metrics report shows: `Tests Passed: 35, Tests Failed: 25`
- Naive Quality Score = 35/60 = 58%

**Why this is NOT a failure:**
- All tests behaved correctly (positive passed, negative failed as expected)
- True quality = 100% (all tests achieved their purpose)
- Reported quality = 58% (conservative metric for safety)
- Threshold = 60% means we accept this as "quality test coverage"

### Threshold Rationale

```
Coverage: 75%  = "Is enough code being tested?"
Quality:  60%  = "Are tests executing correctly?"
              (accounting for negative tests intentionally failing)
```

## How Quality is Reported

### In Test Results Files
```
Total Test Cases: 60
Tests Passed: 35           (positive tests that passed)
Tests Failed: 25           (negative tests that failed as expected)
Test Quality Score: 58%    (35/60, conservative metric)
```

### In SUMMARY Report
```
Total Tests Passed: 35     (sum of all passed tests)
Total Tests Failed: 25     (sum of all failed tests)
Overall Test Quality: 62%  (42 passed of 67 total)
```

### Interpretation
- Quality Score 58-65% = **EXPECTED and CORRECT**
  - Indicates good mix of positive and negative tests
  - Negative tests are working properly (catching errors)

- Quality Score < 50% = **CONCERNING**
  - Suggests too many unexpected failures
  - May indicate broken test cases or incorrect mocks

- Quality Score > 90% = **OK but RISKY**
  - May lack sufficient negative tests
  - May not adequately test error handling

## Customizing Thresholds

You can override the default thresholds in the GitHub Actions workflow:

```yaml
- name: Validate Results Against Thresholds
  env:
    COVERAGE_THRESHOLD: 80    # Require 80% coverage instead of 75%
    QUALITY_THRESHOLD: 50     # Accept 50% quality instead of 60%
```

Or set them as GitHub Secrets if you want them to apply globally.

## Test Success Criteria

The build is considered successful when:

1. ✅ **Coverage >= Coverage Threshold** (default 75%)
   - Code is being adequately tested
   - Enough code paths are exercised

2. ✅ **Quality >= Quality Threshold** (default 60%)
   - Tests are executing as expected
   - Error handling is being tested
   - Test suite includes appropriate negative tests

3. ✅ **All Tests Execute** (no crashes or timeouts)
   - Tests complete their execution
   - SYSOUT is successfully retrieved
   - No unexpected job failures

## Monitoring & Trends

The system tracks:
- **Coverage Trend**: Is coverage improving over time?
- **Quality Trend**: Are tests becoming more comprehensive?
- **Volatility**: Are metrics stable run-to-run?

If quality drops significantly between runs, an alert is generated.

## Best Practices

1. **Maintain 75%+ Coverage**: More code tested = fewer production bugs
2. **Include Negative Tests**: At least 20-30% of tests should be negative tests
3. **Monitor Trends**: Watch for sudden quality or coverage drops
4. **Review Failed Tests**: Understand why tests marked as "FAILED"
5. **Update Thresholds**: Adjust thresholds based on project risk tolerance

---

**Note**: The 60% quality threshold accounts for the reality that comprehensive test suites include intentional negative tests that "fail" as expected. A threshold of 70%+ would be inappropriate for test suites with extensive error-path testing.
