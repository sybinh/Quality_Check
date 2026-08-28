---
name: rq1-validation
description: 'Run PRPL rule validation on RQ1 items. Use when user asks to validate, check, or scan their RQ1 items against PRPL rules. Handles QAM, QAMi, BBM rule sets for BC, IFD, Release, Workitem types.'
argument-hint: 'NTID or command like "validate DAB5HC" or "check all rules"'
---

# RQ1 PRPL Validation

## When to Use

- User asks to validate/check RQ1 items
- User wants to know their PRPL compliance status
- User asks about specific rule violations
- User wants to run validation for team members

## Procedure

### 1. Pre-flight Check

Verify environment is ready:
- `.env` file exists with RQ1_USER, RQ1_PASSWORD
- Python venv is activated or exe is available at `output/executables/`

### 2. Run Validation

```powershell
# Single user
python validate_user_items.py --target_users <NTID>

# Multiple users
python validate_user_items.py --target_users <NTID1>,<NTID2>

# Specific rules only
python validate_user_items.py --target_users <NTID> --rules "PRPL 01,PRPL 11,PRPL 13"
```

**Full CLI reference**: See [usage guide](./references/usage-guide.md) for all options, .env configuration, password caching, rule presets, and troubleshooting.

### 3. Format Output

Transform raw tool output into the standardized report format (see agent instructions). Every validation result must follow the exact template regardless of which model or user is running it.

### 4. Interpret Results

- **WARNING** = affects pass rate, must fix before review
- **INFO** = informational only, no action needed
- Pass rate = (total_checks - WARNING_count) / total_checks * 100

## Available Rules

All 12 rules in `rules/` directory:
- PRPL 01, 02, 03, 06, 07, 11, 12, 13, 14, 15, 16, 18

## Rule Details

For full rule logic, validation conditions, and fix instructions, see [rules reference](./references/rules-reference.md).

## Troubleshooting

| Error | Fix |
|-------|-----|
| AUTH | Wrong username/password, re-enter credentials |
| CONNECTION | Check VPN and network |
| TIMEOUT | Server slow, retry |
| SERVER_ERROR | RQ1 maintenance, try later |
