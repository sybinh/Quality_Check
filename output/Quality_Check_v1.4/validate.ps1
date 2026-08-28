# Quality Check Tool - PowerShell Wrapper with Auto Password Caching
# Handles password prompting once per session; all other args are forwarded to the exe.
#
# Usage examples:
#   .\validate.ps1 --target_users DAB5HC,TRE5HC
#   .\validate.ps1 --user DAB5HC --target_users DAB5HC,TRE5HC --project_id RQONE00001940
#   .\validate.ps1 --rules "PRPL 01,PRPL 11" --target_users DAB5HC
#   .\validate.ps1 DAB5HC   (legacy: single positional username)

# Prompt for password if not cached in current session
if (-not $env:RQ1_PASSWORD) {
    Write-Host "Enter password once for this terminal session" -ForegroundColor Yellow
    
    $securePassword = Read-Host "Enter RQ1 password" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $env:RQ1_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    
    Write-Host "Password cached for this terminal session" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Using cached password from session" -ForegroundColor Green
}

# Run the executable, forwarding all arguments
$exePath = Join-Path $PSScriptRoot "validate_user_items.exe"
& $exePath @args

# Check exit code and show targeted message
$exitCode = $LASTEXITCODE

switch ($exitCode) {
    0 { }  # success
    2 {
        Write-Host "`n[ERROR:AUTH] Wrong username or password." -ForegroundColor Red
        Write-Host "  Clearing cached password - re-run to enter again." -ForegroundColor Yellow
        Remove-Item Env:\RQ1_PASSWORD -ErrorAction SilentlyContinue
    }
    3 {
        Write-Host "`n[ERROR:CONNECTION] Cannot reach RQ1 server." -ForegroundColor Red
        Write-Host "  Check your VPN connection and try again." -ForegroundColor Yellow
    }
    4 {
        Write-Host "`n[ERROR:SERVER_ERROR] RQ1 server returned an error." -ForegroundColor Red
        Write-Host "  The server may be under maintenance. Try again later." -ForegroundColor Yellow
    }
    5 {
        Write-Host "`n[ERROR:TIMEOUT] Connection timed out." -ForegroundColor Red
        Write-Host "  Check your network and try again." -ForegroundColor Yellow
    }
    6 {
        Write-Host "`n[ERROR:SSL] SSL/TLS certificate error." -ForegroundColor Red
        Write-Host "  Your certificate may be outdated." -ForegroundColor Yellow
    }
    default {
        if ($exitCode -ne 0) {
            Write-Host "`n[ERROR] Validation failed (exit code: $exitCode)." -ForegroundColor Red
        }
    }
}

exit $exitCode
