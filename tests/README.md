# Tests for RQ1 PRPL Validation Tool

This folder contains isolated test scripts for individual PRPL rules.

## Structure

```
tests/
??? README.md (this file)
??? test_rule_prpl_06_isolated.py  # Rule 06: IFD defect attributes (ISOLATED)
??? test_rule_prpl_18_isolated.py  # Rule 18: IFD-ISW commitment delay (ISOLATED)
??? test_rule06_closed_ifd.py      # Legacy Rule 06 test
??? test_rule18.py                 # Legacy test (to be deprecated)
```

## Running Tests

### Prerequisites

1. Configure `.env` file with RQ1 credentials:
```bash
RQ1_USER=your_username
RQ1_PASSWORD=your_password
```

2. Activate virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

### Run Individual Rule Test

**Rule 06 (Isolated Test):**
```bash
python tests/test_rule_prpl_06_isolated.py
```

**Rule 18 (Isolated Test):**
```bash
python tests/test_rule_prpl_18_isolated.py
```

## Test Structure

Each test file follows this pattern:

1. **Test Configuration** - Define test cases with expected results
2. **Helper Functions** - Fetch and prepare test data
3. **Test Runner** - Execute tests and compare results
4. **Summary** - Report pass/fail status

### Example Test Case

```python
TEST_CASES = {
    "case_1_delayed": {
        "ifd_id": "RQONE04984940",
        "description": "IFD committed >5 days after ISW",
        "expected": "FAIL"
    }
}
```

## Adding New Tests

To test a new rule, create `test_rule_prpl_XX_<name>.py`:

```python
#!/usr/bin/env python3
"""Isolated test for PRPL Rule XX."""

# 1. Setup imports and environment
# 2. Define TEST_CASES
# 3. Write helper functions
# 4. Implement test runner
# 5. Add summary output
```

## Best Practices

? **DO:**
- Use descriptive test case names
- Document expected behavior
- Separate test data from test logic
- Print clear pass/fail messages
- Exit with appropriate codes (0=pass, 1=fail)

? **DON'T:**
- Hard-code credentials
- Mix multiple rules in one test (keep isolated)
- Leave old/unused test files
- Commit sensitive data

## Maintenance

- **Clean up:** Remove deprecated test files regularly
- **Document:** Update this README when adding new tests
- **Organize:** Keep one file per rule for easy navigation
