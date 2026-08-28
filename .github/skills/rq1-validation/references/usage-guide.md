# Usage Guide

Complete guide for running RQ1 PRPL validation tool via CLI or executable.

---

## Installation

### Python Script Mode
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run directly
python validate_user_items.py [options]
```

### Standalone Executable Mode
```powershell
# Navigate to release folder
cd output\executables

# Run via PowerShell wrapper (caches password)
.\validate.ps1 <NTID>

# Or run exe directly
.\validate_user_items.exe [options]
```

---

## CLI Options

### Basic Usage

```powershell
# Validate single user
python validate_user_items.py --target_users <NTID>

# Validate multiple users
python validate_user_items.py --target_users <NTID1>,<NTID2>,<NTID3>

# Legacy positional argument (single user only)
python validate_user_items.py <NTID>
```

### Full Options Reference

| Option | Description | Example | Env Fallback |
|--------|-------------|---------|--------------|
| `--user` | Login username (authenticates to RQ1) | `--user DAB5HC` | `RQ1_USER` |
| `--password` | Login password (avoid in CLI, use .env) | `--password MyPass` | `RQ1_PASSWORD` |
| `--target_users` | Comma-separated NTIDs to validate | `--target_users ABC,XYZ` | `RQ1_MEMBERS` |
| `--project_id` | Comma-separated project IDs for scope | `--project_id RQONE00001940` | `RQ1_PROJECT_IDS` |
| `--rules` | Comma-separated rule IDs to apply | `--rules "PRPL 01,PRPL 11"` | `RQ1_RULES` |

### Examples

```powershell
# Validate specific user with specific rules only
python validate_user_items.py --target_users TYH5HC --rules "PRPL 11,PRPL 13,PRPL 18"

# Validate team members for specific project
python validate_user_items.py --target_users "DAB5HC,TRE5HC,ABC1HC" --project_id RQONE00001940

# Login as different user to validate others
python validate_user_items.py --user DAB5HC --target_users TYH5HC,ABC1HC

# Validate yourself with all rules (uses RQ1_USER from .env)
python validate_user_items.py --target_users DAB5HC
```

---

## Environment Configuration (.env)

Create `.env` file in project root:

```ini
# Authentication (required)
RQ1_USER=DAB5HC
RQ1_PASSWORD=YourPasswordHere

# Tool identification (required, do not change)
RQ1_TOOLNAME=OfficeUtils
RQ1_TOOLVERSION=1.0

# Validation scope (optional)
RQ1_PROJECT_IDS=RQONE00001940,RQONE87654321
RQ1_MEMBERS=DAB5HC,TRE5HC,TYH5HC,ABC1HC
RQ1_RULES=PRPL 01,PRPL 11,PRPL 13

# Environment (optional, default: PRODUCTIVE)
RQ1_ENVIRONMENT=PRODUCTIVE
```

### Configuration Details

#### `RQ1_USER` (required)
Your NTID for RQ1 authentication. Used to login and fetch data.

#### `RQ1_PASSWORD` (required)
Your RQ1 password. 

**Security notes**:
- If not in .env, tool will prompt interactively (password is hidden)
- PowerShell wrapper caches password in session: `$env:RQ1_PASSWORD = "..."`
- Never commit .env to git (already in .gitignore)

#### `RQ1_PROJECT_IDS` (optional)
Comma-separated RQ1 project IDs. Used for:
- **PRPL 11** (IFD 5-day SLA): Determines project assignment date for SLA calculation
- Scoping validation to specific projects (if needed in future)

**Format**: `RQONE12345678,RQONE87654321`

If empty, some rules may skip or use fallback dates.

#### `RQ1_MEMBERS` (optional)
Comma-separated NTIDs of team members to validate.

**Behavior**:
- If set: `--target_users` defaults to this list (unless overridden)
- If empty: Only validates the login user (`RQ1_USER`)

**Use case**: Set once for your team, then run validation for everyone:
```powershell
# .env has: RQ1_MEMBERS=DAB5HC,TRE5HC,TYH5HC
python validate_user_items.py  # validates all 3 members
```

#### `RQ1_RULES` (optional)
Comma-separated rule IDs to enable.

**Behavior**:
- If set: Only specified rules are executed
- If empty: All 12 rules are applied

**Format**: `PRPL 01,PRPL 03,PRPL 11,PRPL 13`

**Use case**: Enable subset during development or for specific audits:
```ini
# QAMi rules only (WARNING severity)
RQ1_RULES=PRPL 01,PRPL 02,PRPL 03,PRPL 06,PRPL 07,PRPL 11,PRPL 12,PRPL 13,PRPL 14,PRPL 18

# BBM rules only (BC-focused)
RQ1_RULES=PRPL 01,PRPL 07

# Quick check (critical rules)
RQ1_RULES=PRPL 11,PRPL 14,PRPL 18
```

#### `RQ1_ENVIRONMENT` (optional)
RQ1 server environment. Default: `PRODUCTIVE`

**Options**:
- `PRODUCTIVE` - Live production server
- `ACCEPTANCE` - Test/staging server

Only change if testing against RQ1 acceptance environment.

---

## Password Caching

### Option 1: PowerShell Session Variable
```powershell
# Set once per PowerShell session
$env:RQ1_PASSWORD = "YourPassword"

# Now run multiple validations without re-entering password
python validate_user_items.py --target_users USER1
python validate_user_items.py --target_users USER2
```

### Option 2: .env File
```ini
# .env (NOT committed to git)
RQ1_PASSWORD=YourPassword
```

### Option 3: PowerShell Wrapper (Executable Only)
```powershell
# output/executables/validate.ps1 caches password automatically
.\validate.ps1 DAB5HC
.\validate.ps1 TRE5HC  # reuses cached password
```

---

## Rule Set Presets

Common rule configurations for different validation scenarios:

### QAM (Full Quality Assurance - All 12 rules)
```ini
RQ1_RULES=PRPL 01,PRPL 02,PRPL 03,PRPL 06,PRPL 07,PRPL 11,PRPL 12,PRPL 13,PRPL 14,PRPL 15,PRPL 16,PRPL 18
```
Or leave empty to apply all rules.

### QAMi (QAM Interim - WARNING rules only)
```ini
RQ1_RULES=PRPL 01,PRPL 02,PRPL 03,PRPL 06,PRPL 07,PRPL 11,PRPL 12,PRPL 13,PRPL 14,PRPL 18
```
Excludes PRPL 15, 16 (INFO severity).

### BBM (Build Block Metrics - BC focus)
```ini
RQ1_RULES=PRPL 01,PRPL 07
```

### IFD Focus (Defect tracking)
```ini
RQ1_RULES=PRPL 06,PRPL 11,PRPL 12,PRPL 13,PRPL 14,PRPL 18
```

### SLA Monitoring (Time-sensitive rules)
```ini
RQ1_RULES=PRPL 11,PRPL 18
```

---

## Exit Codes

The tool returns specific exit codes for automation/CI integration:

| Code | Type | Meaning |
|------|------|---------|
| 0 | Success | Validation completed (violations may exist but tool ran successfully) |
| 1 | Generic error | Unknown error |
| 2 | AUTH | Authentication failed (wrong username/password) |
| 3 | CONNECTION | Cannot reach RQ1 server (network/VPN issue) |
| 4 | SERVER_ERROR | RQ1 server error (500/502/503) |
| 5 | TIMEOUT | Request timed out |
| 6 | SSL | SSL/certificate error |
| 7 | FORBIDDEN | Access denied (403) |
| 8 | NOT_FOUND | Resource not found (404) |
| 9 | RATE_LIMIT | Too many requests (429) |

**CI/CD usage**:
```powershell
python validate_user_items.py --target_users $env:CI_USER
if ($LASTEXITCODE -eq 2) {
    Write-Error "Authentication failed - check credentials"
    exit 2
}
if ($LASTEXITCODE -eq 3) {
    Write-Error "Cannot reach RQ1 - check VPN"
    exit 3
}
# ... handle violations from stdout
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'rq1'"
**Cause**: Virtual environment not activated.  
**Fix**: 
```powershell
.\.venv\Scripts\Activate.ps1
python validate_user_items.py ...
```

### "[ERROR:AUTH] Wrong username or password"
**Cause**: Incorrect RQ1 credentials.  
**Fix**: 
- Check `RQ1_USER` in .env
- Delete cached password: `Remove-Item Env:\RQ1_PASSWORD`
- Re-run and enter correct password

### "[ERROR:CONNECTION] Cannot reach RQ1 server"
**Cause**: Network or VPN issue.  
**Fix**:
- Check VPN connection
- Verify network connectivity
- Try accessing RQ1 web interface in browser

### "[ERROR:TIMEOUT] Connection timed out"
**Cause**: RQ1 server slow or network congestion.  
**Fix**: Retry after a moment. Server may be under load.

### "User XYZ not found"
**Cause**: NTID doesn't exist or typo.  
**Fix**: Verify NTID spelling, check RQ1 user exists.

### No violations but expecting some
**Cause**: Wrong rule set or project scope.  
**Fix**: 
- Check `RQ1_RULES` in .env (may be filtering rules)
- Verify `RQ1_PROJECT_IDS` if using PRPL 11 (SLA rule)
- Run with all rules: `python validate_user_items.py --target_users <NTID>` (no --rules)

---

## Output Format

See [rules-reference.md](./rules-reference.md) for detailed rule descriptions.

The tool outputs:
1. **Header** - User, authentication info
2. **Progress** - Item counts by type (IFD, BC, Workitem, etc.)
3. **Summary** - Total checks, pass rate, violation counts
4. **Violations** - Detailed list with item ID, rule, description, fix hints
5. **Footer** - Action summary

All output follows standardized format (enforced by agent) for consistency across models/users.
