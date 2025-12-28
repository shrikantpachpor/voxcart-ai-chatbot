# GitHub Pre-Upload Cleanup Script
# Run this script from the app directory before pushing to GitHub
# Usage: .\scripts\cleanup_for_github.ps1

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "GitHub Pre-Upload Cleanup Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$WarningCount = 0

# Change to app directory if not already there
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptPath
Set-Location $appDir

Write-Host "[1/8] Checking for .env file in git..." -ForegroundColor Yellow
$envInGit = git ls-files 2>$null | Select-String "^\.env$"
if ($envInGit) {
    Write-Host "  ❌ ERROR: .env file is tracked in git!" -ForegroundColor Red
    Write-Host "  Run: git rm --cached .env" -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "  ✓ .env not in git (good!)" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/8] Removing log files..." -ForegroundColor Yellow
$logFiles = Get-ChildItem -Path . -Filter "*.log" -File -Recurse
$logCount = ($logFiles | Measure-Object).Count
if ($logCount -gt 0) {
    $logFiles | Remove-Item -Force
    Write-Host "  ✓ Removed $logCount log file(s)" -ForegroundColor Green
} else {
    Write-Host "  ✓ No log files found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/8] Removing __pycache__ directories..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse
$pycacheCount = ($pycacheDirs | Measure-Object).Count
if ($pycacheCount -gt 0) {
    $pycacheDirs | Remove-Item -Recurse -Force
    Write-Host "  ✓ Removed $pycacheCount __pycache__ director(ies)" -ForegroundColor Green
} else {
    Write-Host "  ✓ No __pycache__ directories found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/8] Removing .pyc files..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Path . -Filter "*.pyc" -File -Recurse
$pycCount = ($pycFiles | Measure-Object).Count
if ($pycCount -gt 0) {
    $pycFiles | Remove-Item -Force
    Write-Host "  ✓ Removed $pycCount .pyc file(s)" -ForegroundColor Green
} else {
    Write-Host "  ✓ No .pyc files found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/8] Removing .pyo and .pyd files..." -ForegroundColor Yellow
$pyoFiles = Get-ChildItem -Path . -Filter "*.pyo" -File -Recurse
$pydFiles = Get-ChildItem -Path . -Filter "*.pyd" -File -Recurse
$pyoCount = ($pyoFiles | Measure-Object).Count
$pydCount = ($pydFiles | Measure-Object).Count
$totalPyFiles = $pyoCount + $pydCount
if ($totalPyFiles -gt 0) {
    $pyoFiles | Remove-Item -Force
    $pydFiles | Remove-Item -Force
    Write-Host "  ✓ Removed $totalPyFiles compiled Python file(s)" -ForegroundColor Green
} else {
    Write-Host "  ✓ No .pyo/.pyd files found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[6/8] Checking for .db and .sqlite files..." -ForegroundColor Yellow
$dbFiles = Get-ChildItem -Path . -File -Recurse | Where-Object { $_.Extension -match "\.(db|sqlite)$" }
$dbCount = ($dbFiles | Measure-Object).Count
if ($dbCount -gt 0) {
    Write-Host "  ⚠️  WARNING: Found $dbCount database file(s):" -ForegroundColor Yellow
    $dbFiles | ForEach-Object { Write-Host "    - $($_.FullName)" -ForegroundColor Yellow }
    Write-Host "  Consider adding to .gitignore if these are local dev databases" -ForegroundColor Yellow
    $WarningCount++
} else {
    Write-Host "  ✓ No database files found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[7/8] Verifying .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    $requiredPatterns = @("*.log", "*.pyc", ".env", "__pycache__")
    $missingPatterns = @()
    
    foreach ($pattern in $requiredPatterns) {
        if ($gitignoreContent -notmatch [regex]::Escape($pattern)) {
            $missingPatterns += $pattern
        }
    }
    
    if ($missingPatterns.Count -gt 0) {
        Write-Host "  ⚠️  WARNING: .gitignore missing patterns:" -ForegroundColor Yellow
        $missingPatterns | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
        $WarningCount++
    } else {
        Write-Host "  ✓ .gitignore has all required patterns" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ ERROR: .gitignore file not found!" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""
Write-Host "[8/8] Checking git repository status..." -ForegroundColor Yellow
try {
    $gitStatus = git status --short 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠️  WARNING: Git repository may have issues" -ForegroundColor Yellow
        Write-Host "  Error: $gitStatus" -ForegroundColor Yellow
        Write-Host "  Consider running: git fsck --full" -ForegroundColor Yellow
        $WarningCount++
    } else {
        Write-Host "  ✓ Git repository is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️  WARNING: Could not check git status" -ForegroundColor Yellow
    $WarningCount++
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Errors: $ErrorCount" -ForegroundColor $(if ($ErrorCount -gt 0) { "Red" } else { "Green" })
Write-Host "Warnings: $WarningCount" -ForegroundColor $(if ($WarningCount -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($ErrorCount -gt 0) {
    Write-Host "❌ CRITICAL ERRORS FOUND - Fix these before pushing!" -ForegroundColor Red
    Write-Host ""
    exit 1
} elseif ($WarningCount -gt 0) {
    Write-Host "⚠️  WARNINGS FOUND - Review these before pushing" -ForegroundColor Yellow
    Write-Host ""
    exit 0
} else {
    Write-Host "✅ All checks passed! Repository is clean." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Review git status: git status" -ForegroundColor White
    Write-Host "2. Commit your changes: git add . && git commit -m 'Your message'" -ForegroundColor White
    Write-Host "3. Optional: Run gitleaks scan: .\scripts\run_gitleaks.ps1" -ForegroundColor White
    Write-Host "4. Push to GitHub: git push" -ForegroundColor White
    Write-Host ""
    exit 0
}
