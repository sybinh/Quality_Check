# Running Modes

This document covers all supported ways to run the RQ1 PRPL validation tool, including interactive CLI, standalone executable, headless/JSON output, multi-user batch validation, and the Copilot agent interface.

---

## Overview

| Mode | Entry Point | Use Case |
|------|-------------|----------|
| Executable (interactive) | `validate.ps1` | Daily use, end users with no Python setup |
| Python CLI (interactive) | `validate_user_items.py` | Development, testing new rules |
| JSON to stdout | `--json` flag | Piping output to other scripts or tools |
| JSON to file | `--output` flag | Saving reports, CI pipelines |
| Multi-user batch | `--target_users` / `RQ1_MEMBERS` | Validating a whole team at once |
| Rule-filtered | `--rules` flag | Checking a specific subset of PRPL rules |
| Copilot agent | `@rq1-validator` in VS Code | Chat-based validation and rule explanation |

---

## Mode 1: Standalone Executable (Interactive)

The packaged executable requires no Python installation. It is the recommended mode for engineers who only need to run validations, not modify rules.

**Location**: `output/executables/`

**Files required**:
- `validate.ps1` - PowerShell wrapper with password caching
- `validate_user_items.exe` - compiled tool
- `.env` - credentials and configuration

**Setup** (first time on a new machine):

```powershell
cd output\executables
Copy-Item .env.example .env
notepad .env
```

Minimum `.env` content:

```ini
RQ1_USER=YOUR_NTID
RQ1_PROJECT_IDS=RQONE00001940
```

**Running**:

```powershell
# Validate yourself
.\validate.ps1 --target_users YOUR_NTID

# Validate another user
.\validate.ps1 --target_users TYH5HC

# Validate multiple users
.\validate.ps1 --target_users DAB5HC,TRE5HC,TYH5HC

# Run with specific rules only
.\validate.ps1 --target_users DAB5HC --rules "PRPL 11,PRPL 13,PRPL 18"

# Legacy single-argument form (still supported)
.\validate.ps1 DAB5HC
```

**Password behavior**:

The wrapper prompts for password on first run of a terminal session. The password is stored in the process environment variable `RQ1_PASSWORD` and reused for all subsequent runs in that session. It is never written to disk.

```
First run:
  Enter password once for this terminal session
  Enter RQ1 password: ****
  Password cached for this terminal session

Subsequent runs:
  Using cached password from session
```

If the wrong password is entered, the tool exits with code 2 and the wrapper clears the cached password automatically, prompting again on the next run.

---

## Mode 2: Python CLI (Interactive)

For development and testing. Requires the virtual environment to be activated.

**Setup**:

```powershell
# From project root
.\.venv\Scripts\Activate.ps1
```

**Basic usage**:

```powershell
python validate_user_items.py --target_users <NTID>
```

**All available options**:

| Flag | Description | Falls back to |
|------|-------------|---------------|
| `--user NTID` | Login username for authentication | `RQ1_USER` in `.env` |
| `--password PASSWORD` | Login password (avoid in scripts) | `RQ1_PASSWORD` in `.env` / interactive prompt |
| `--target_users NTID,...` | Comma-separated NTIDs to validate | `RQ1_MEMBERS` in `.env`, then `RQ1_USER` |
| `--project_id RQONE,...` | Comma-separated project IDs | `RQ1_PROJECT_IDS` in `.env` |
| `--rules "PRPL XX,..."` | Rule IDs to apply | `RQ1_RULES` in `.env`, then all 12 rules |
| `--json` | Output JSON to stdout instead of text summary | - |
| `--output FILE.json` | Write JSON to file (text still prints) | - |

**Examples**:

```powershell
# Validate single user, all rules
python validate_user_items.py --target_users DAB5HC

# Validate with a different login account
python validate_user_items.py --user DAB5HC --target_users TYH5HC

# Only IFD-related rules
python validate_user_items.py --target_users DAB5HC --rules "PRPL 06,PRPL 11,PRPL 12,PRPL 13,PRPL 14,PRPL 18"

# Scope PRPL 11 SLA calculation to specific project
python validate_user_items.py --target_users DAB5HC --project_id RQONE00001940
```

---

## Mode 3: JSON Output to Stdout (Headless)

Produces a machine-readable JSON object to stdout in place of the formatted text summary. Progress messages (lookup, query steps) still print to stdout before the JSON block, so redirect or filter as needed in scripts.

**Usage**:

```powershell
python validate_user_items.py --target_users TYH5HC --json
# or with executable:
.\validate_user_items.exe --target_users TYH5HC --json
```

**Output structure**:

```json
{
  "user": "TYH5HC",
  "full_name": "Nguyen Ba Vu Thach (MS/EPC22-PS)",
  "validated_at": "2026-08-28T16:58:15",
  "authenticated_as": "DAB5HC",
  "rules_applied": ["PRPL 01", "PRPL 02", "PRPL 03", "..."],
  "summary": {
    "total_items": 10,
    "items": {
      "issues":   { "total": 1, "IFD": 1, "ISW": 0, "Other": 0 },
      "releases": { "total": 3, "BC": 0, "BX": 0, "FC": 3, "PVER": 0, "PVAR": 0, "Other": 0 },
      "workitems": 6
    },
    "total_checks": 29,
    "pass_rate": 100.0,
    "violations_total": 2,
    "violations_warning": 0,
    "violations_info": 2
  },
  "violations": [
    {
      "index": 1,
      "rule": "PRPL 03",
      "rule_id": "PRPL 03.00.00",
      "severity": "INFO",
      "item_id": "RQONE04889864",
      "item_title": "FC-ARB : ComScl_NetMtrx / 709.310.0",
      "description": "Release RQONE04889864 is in 'Conflicted' state. ..."
    }
  ]
}
```

**Extracting specific fields with PowerShell**:

```powershell
$result = python validate_user_items.py --target_users TYH5HC --json |
    Select-String -Pattern '^\{' -Context 0,999 |
    ForEach-Object { $_.Line + $_.Context.PostContext -join "`n" } |
    ConvertFrom-Json

$result.summary.pass_rate        # 100.0
$result.summary.violations_warning  # 0
$result.violations | Format-Table rule_id, severity, item_id
```

---

## Mode 4: JSON Output to File

Writes the JSON report to a file while still printing the normal text summary to the terminal. Useful for keeping a history of validation runs or feeding results into other tools.

**Usage**:

```powershell
python validate_user_items.py --target_users DAB5HC --output report.json
# or
.\validate_user_items.exe --target_users DAB5HC --output report.json
```

The file is created or overwritten in the current working directory.

**Multi-user output**: When validating multiple users with `--output`, the filename is prefixed with each NTID automatically to avoid overwrites:

```powershell
python validate_user_items.py --target_users DAB5HC,TRE5HC --output report.json
# Creates: DAB5HC_report.json, TRE5HC_report.json
```

**Combining with --json**: `--json` and `--output` can be used together. `--json` controls stdout, `--output` controls file writing.

```powershell
python validate_user_items.py --target_users DAB5HC --json --output report.json
```

---

## Mode 5: Multi-User Batch Validation

Validates multiple users in a single run. Each user produces a separate validation output block.

**Via CLI**:

```powershell
python validate_user_items.py --target_users DAB5HC,TRE5HC,TYH5HC
```

**Via .env** (validate the whole team without specifying users each time):

```ini
RQ1_MEMBERS=DAB5HC,TRE5HC,TYH5HC,ABC1HC
```

Then run with no `--target_users` argument:

```powershell
python validate_user_items.py
# validates all four members listed in RQ1_MEMBERS
```

The `.env` value is overridden if `--target_users` is passed on the command line.

---

## Mode 6: Rule-Filtered Validation

Run only a specific subset of the 12 rules. Useful for targeted audits or checking a single rule after a fix.

**Via CLI**:

```powershell
python validate_user_items.py --target_users DAB5HC --rules "PRPL 11,PRPL 18"
```

**Via .env** (applies to all runs until changed):

```ini
RQ1_RULES=PRPL 01,PRPL 07
```

**Common presets**:

| Preset | Rules | Purpose |
|--------|-------|---------|
| QAM full | all 12 | Complete audit before QAM review |
| QAMi | 01,02,03,06,07,11,12,13,14,18 | WARNING-only rules (excludes INFO) |
| BBM | 01,07 | BC-focused metrics |
| IFD defect tracking | 06,11,12,13,14,18 | All IFD-related rules |
| SLA monitoring | 11,18 | Time-sensitive rules only |
| Closure check | 12,13,15,16 | Items that should be closed |

---

## Mode 7: Copilot Agent (VS Code)

The `rq1-validator` agent is available in VS Code Copilot Chat. It runs the validation tool and formats the output as a standardized report.

**Invocation**:

```
@rq1-validator validate TYH5HC
@rq1-validator validate DAB5HC,TRE5HC with rules PRPL 11 and PRPL 13
@rq1-validator explain PRPL 14
@rq1-validator what does rule 06 check
```

The agent uses the same underlying Python script, so it requires:
- The virtual environment to be accessible
- `.env` with valid credentials in the project root

**What the agent does**:

1. Parses the user request to extract NTIDs, rule filters, and intent
2. Runs `validate_user_items.py` via terminal
3. Formats the raw output into the standardized report (see below)
4. Explains violations and suggests fixes on request

**Standardized report format** (consistent across all models and users):

```
================================================================================
PRPL VALIDATION REPORT
================================================================================
User: TYH5HC (Nguyen Ba Vu Thach)
Date: 2026-08-28
Rules Applied: PRPL 01, 02, 03, 06, 07, 11, 12, 13, 14, 15, 16, 18
================================================================================

ITEMS SCANNED
  Issues:    1 (IFD: 1)
  Releases:  3 (FC: 3)
  Workitems: 6
  Total:     10

RESULTS
  Checks performed: 29
  Pass rate:        100.0% (WARNING-based)
  Violations:       2 (WARNING: 0, INFO: 2)

================================================================================
VIOLATIONS
================================================================================

[1] PRPL 03.00.00 | INFO
    Item:   RQONE04889864
    Title:  FC-ARB : ComScl_NetMtrx / 709.310.0
    Rule:   Item in Conflicted state must be resolved
    Detail: Release is in 'Conflicted' state. Resolve when clarification is complete.

================================================================================
SUMMARY
================================================================================
Action Required: 0 WARNING violations.
INFO items: 2 (informational, no action needed).
================================================================================
```

The agent always uses this format regardless of which underlying model (GPT-4o, Claude, etc.) is active.

---

## Environment Variables Reference

All configuration is read from `.env` in the project root (or `output/executables/.env` for the packaged release).

| Variable | Required | Description |
|----------|----------|-------------|
| `RQ1_USER` | Yes | NTID used for authentication |
| `RQ1_PASSWORD` | No | Password (prompted if missing; not recommended to store in file) |
| `RQ1_PROJECT_IDS` | Recommended | Comma-separated project IDs; used by PRPL 11 for SLA baseline |
| `RQ1_MEMBERS` | No | Default list of NTIDs to validate when no `--target_users` is given |
| `RQ1_RULES` | No | Restrict which rules run; leave empty to apply all 12 |
| `RQ1_TOOLNAME` | No | Identifier reported to RQ1 server (default: `OfficeUtils`) |
| `RQ1_TOOLVERSION` | No | Version reported to RQ1 server (default: `1.0`) |
| `RQ1_ENVIRONMENT` | No | `PRODUCTIVE` or `ACCEPTANCE` (default: `PRODUCTIVE`) |

---

## Exit Codes

The tool returns structured exit codes for scripting and CI integration.

| Code | Label | Meaning |
|------|-------|---------|
| 0 | Success | Validation completed (violations may exist) |
| 2 | AUTH | Wrong username or password |
| 3 | CONNECTION | Cannot reach RQ1 server |
| 4 | SERVER_ERROR | RQ1 returned 500/502/503 |
| 5 | TIMEOUT | Request timed out |
| 6 | SSL | Certificate or TLS error |
| 7 | FORBIDDEN | Access denied (403) |
| 8 | NOT_FOUND | Resource not found (404) |
| 9 | RATE_LIMIT | Too many requests (429) |

Exit code 0 does not mean zero violations. It means the tool ran successfully. Check `violations_warning` in JSON output or the pass rate in text output to determine compliance status.

**PowerShell example**:

```powershell
python validate_user_items.py --target_users DAB5HC
if ($LASTEXITCODE -eq 2) {
    Write-Error "Authentication failed"
    exit 2
}
if ($LASTEXITCODE -eq 3) {
    Write-Error "Cannot reach RQ1 server - check network"
    exit 3
}
```

---

## Proxy Considerations

The tool uses the system HTTP proxy by default (via `http_proxy` / `https_proxy` environment variables). If the proxy is set but not reachable (for example, a local proxy like `127.0.0.1:3128` that is not running), connections will fail with a `ProxyError`.

To bypass a broken proxy for the current session:

```powershell
$env:HTTPS_PROXY = ""
$env:HTTP_PROXY  = ""
$env:https_proxy = ""
$env:http_proxy  = ""
python validate_user_items.py --target_users DAB5HC
```

To persist this in `.env` (clears proxy for all runs):

```ini
HTTPS_PROXY=
HTTP_PROXY=
```
