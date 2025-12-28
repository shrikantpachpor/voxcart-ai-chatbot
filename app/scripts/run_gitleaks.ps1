<#
PowerShell helper to run gitleaks locally.
Install gitleaks (https://github.com/zricethezav/gitleaks) first.
#>
if (-not (Get-Command gitleaks -ErrorAction SilentlyContinue)) {
    Write-Host "gitleaks not found. Install from https://github.com/zricethezav/gitleaks or via Scoop/Chocolatey."
    exit 1
}

Write-Host "Running gitleaks detect --source ."
gitleaks detect --source .
