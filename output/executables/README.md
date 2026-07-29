# Quality Check Tool

Version 1.4 — Automated validation for 12 PRPL rules against RQ1 items.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [CLI Reference](#cli-reference)
5. [Rules](#rules)
6. [Output](#output)
7. [Error Codes](#error-codes)
8. [Troubleshooting](#troubleshooting)
9. [Changelog](#changelog)
10. [Files Included](#files-included)

---

## Quick Start

1. Copy `.env.example` to `.env` and fill in your details:

```ini
RQ1_USER=your_ntid
RQ1_PROJECT_IDS=RQONE00001940
```

2. Run validation:

```powershell
.\validate.ps1 --target_users YOUR_NTID
```

---

## Configuration

Settings are read from the `.env` file in the tool directory. CLI arguments override `.env` values.

| Variable | Required | Description |
|----------|----------|-------------|
| `RQ1_USER` | Yes | Your RQ1 login NTID |
| `RQ1_PROJECT_IDS` | Yes | Comma-separated RQ1 project IDs (e.g. `RQONE00001940`) |
| `RQ1_MEMBERS` | No | Comma-separated NTIDs to validate. Defaults to `RQ1_USER`. |
| `RQ1_RULES` | No | Comma-separated rule IDs to run. Defaults to all 12 rules. |

`RQ1_PASSWORD` is never stored in `.env`. The tool prompts on first run and caches the password for the terminal session only.

### Example .env

```ini
RQ1_USER=DAB5HC
RQ1_PROJECT_IDS=RQONE00001940,RQONE00002345

# Optional: validate a team without specifying on the command line
RQ1_MEMBERS=DAB5HC,TRE5HC,ABC1HC

# Optional: run only a subset of rules
# RQ1_RULES=PRPL 01,PRPL 11,PRPL 14
```

---

## Usage

### PowerShell Wrapper (Recommended)

`validate.ps1` handles password prompting and session caching. The password is stored in memory only and cleared when the terminal is closed.

```powershell
# Validate a single user
.\validate.ps1 --target_users DAB5HC

# Validate multiple users
.\validate.ps1 --target_users DAB5HC,TRE5HC,ABC1HC

# Run specific rules only
.\validate.ps1 --target_users DAB5HC --rules "PRPL 01,PRPL 11"

# Override project ID at runtime
.\validate.ps1 --target_users DAB5HC --project_id RQONE00001940

# Legacy usage (single positional argument, still supported)
.\validate.ps1 DAB5HC
```

### Direct Executable

```powershell
# Interactive (prompts for password)
.\validate_user_items.exe --target_users DAB5HC

# Non-interactive (for automation/scripting)
.\validate_user_items.exe --user ABC1HC --password MyPass --target_users ABC1HC,DEF2HC

# Show help
.\validate_user_items.exe --help
```

---

## CLI Reference

All arguments are optional if the corresponding `.env` variable is set.

| Argument | Fallback (.env) | Description |
|----------|-----------------|-------------|
| `--user NTID` | `RQ1_USER` | Login username (NTID) |
| `--password PASSWORD` | `RQ1_PASSWORD` | Authentication password |
| `--target_users NTID[,...]` | `RQ1_MEMBERS` | Comma-separated NTIDs to validate |
| `--project_id RQONE[,...]` | `RQ1_PROJECT_IDS` | Comma-separated project IDs |
| `--rules "PRPL XX[,...]"` | `RQ1_RULES` | Comma-separated rule IDs to apply |

Priority order: CLI argument > `.env` variable > default behavior

---

## Rules

| Rule | Severity | Description |
|------|----------|-------------|
| PRPL 01 | WARNING | BC-R not in Requested state 8 weeks before PVER planned delivery date |
| PRPL 02 | WARNING | Workitem in Started state without a planned date in the planning tab |
| PRPL 03 | INFO | Item is in Conflicted state |
| PRPL 06 | WARNING | IFD defect detection/injection attributes are incomplete |
| PRPL 07 | WARNING | BC planned date is later than the requested delivery date of a mapped PVER/PVAR |
| PRPL 11 | WARNING | IFD 5-day evaluation SLA exceeded |
| PRPL 12 | WARNING | IFD not closed after all mapped BC-Rs are closed or cancelled |
| PRPL 13 | WARNING | IFD not implemented or closed after BC-R planned date |
| PRPL 14 | WARNING | IFD not committed while parent ISW is committed |
| PRPL 15 | WARNING | Release not closed after planned date (all types: BC, BX, FC, FX, PVER, PVAR) |
| PRPL 16 | WARNING | Workitem not closed after planned date |
| PRPL 18 | WARNING | IFD not committed 5 or more working days after parent ISW was committed |

Severity meanings:
- **WARNING** — violation that affects pass rate; action required
- **INFO** — informational finding; does not affect pass rate

---

## Output

### Summary Block

```
Total items assigned: 31
  - Issues: 7 (IFD=6, ISW=1)
  - Releases: 9 (BC=8, FC=1)
  - Workitems: 15
Total checks performed: 104
Rules applied: 01, 02, 03, 06, 07, 11, 12, 13, 14, 15, 16, 18
Violations found: 18 (WARNING: 8, INFO: 10)
Pass rate: 92.3% (based on WARNING violations)
```

### Pass Rate Formula

```
Pass rate = (Total checks - WARNING violations) / Total checks * 100%
```

---

## Error Codes

The tool returns a specific exit code for each error category, usable in scripts via `$LASTEXITCODE`.

| Exit Code | Code | Cause | Action |
|-----------|------|-------|--------|
| 0 | — | Success | — |
| 2 | AUTH | Wrong username or password | Re-run; password cache is cleared automatically |
| 3 | CONNECTION | Cannot reach RQ1 server | Check VPN connection |
| 4 | SERVER_ERROR | RQ1 server error (5xx) | Server may be under maintenance; try again later |
| 5 | TIMEOUT | Connection timed out | Check network connection and retry |
| 6 | SSL | SSL/TLS certificate error | Check certificate validity |
| 7 | FORBIDDEN | Access denied (403) | Verify account permissions |
| 8 | NOT_FOUND | Resource not found (404) | Check item IDs |
| 9 | RATE_LIMIT | Too many requests (429) | Wait and retry |
| 1 | UNKNOWN | Unexpected error | See full terminal output |

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|---------|
| `[ERROR:AUTH]` | Wrong password | Re-run; the password cache is cleared automatically |
| `[ERROR:CONNECTION]` | VPN disconnected | Connect to VPN and retry |
| `[ERROR:SERVER_ERROR]` | Server under maintenance | Wait and retry |
| `[ERROR:TIMEOUT]` | Slow or unstable network | Check connection and retry |
| No items found | Wrong project ID | Verify `RQ1_PROJECT_IDS` in `.env` |
| Wrong cached password | Stale cached value | Run `Remove-Item Env:\RQ1_PASSWORD` and retry |

### Clear Cached Password

```powershell
Remove-Item Env:\RQ1_PASSWORD
```

---

## Report an Issue

https://github.com/sybinh/Quality_Check/issues/new

Include in the report:
- Your NTID
- Rule that triggered incorrectly (e.g. PRPL 15)
- Item ID (e.g. RQONE04659895)
- Full terminal output

---

## Changelog

### Version 1.4
- New: CLI interface (`--user`, `--password`, `--target_users`, `--project_id`, `--rules`)
- New: `RQ1_MEMBERS` in `.env` for team validation without CLI arguments
- New: `RQ1_RULES` in `.env` to run a subset of rules; disabled rules are fully skipped including their API calls
- New: Typed exit codes (2-9) for each error category
- New: Structured error messages with actionable hints per error type

### Version 1.3 (Apr 6, 2026)
- Fix: PRPL 01 now runs correctly (was silently skipped in all previous versions)
- Fix: PRPL 15 now covers all release types (BC, BX, FC, FX, PVER, PVAR), not just BC and FC
- Fix: PRPL 15 was reading a wrong field and never triggering
- Fix: Code reliability improvements (NameError guard, redundant condition removed)

### Version 1.2 (Jan 8, 2026)
- Auto password caching via PowerShell wrapper script
- Password masking during input
- Clear authentication error messages

### Version 1.1
- 12 PRPL rules implementation
- Standalone executable package

---

## Files Included

| File | Description |
|------|-------------|
| `validate.ps1` | PowerShell wrapper with password caching |
| `validate_user_items.exe` | Main validation executable |
| `README.md` | This file |
| `.env.example` | Configuration template |