<#
PowerShell helper to purge sensitive files from git history using git-filter-repo.
Run from the repository root (one level above `app/`).

WARNING: This will rewrite git history. Create a backup clone before running.
#>

param(
    [string[]] $PathsToRemove = @('app/.env','app/chatbot_logs.log')
)

function Ensure-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "git is not installed or not in PATH. Aborting."
        exit 1
    }
}

function Ensure-PythonTool {
    if (-not (Get-Command git-filter-repo -ErrorAction SilentlyContinue)) {
        Write-Host "git-filter-repo not found. Installing via pip..."
        python -m pip install --user git-filter-repo
        if (-not (Get-Command git-filter-repo -ErrorAction SilentlyContinue)) {
            Write-Error "git-filter-repo still not found. Ensure it is installed and accessible."
            exit 1
        }
    }
}

Ensure-Git
Ensure-PythonTool

Write-Host "This script will rewrite git history and remove: $($PathsToRemove -join ', ')"
Write-Host "Create a backup clone before proceeding. Example: git clone --mirror . ../repo-backup.git"
Write-Host "Continue? (y/N)"
$c = Read-Host
if ($c -ne 'y') { Write-Host 'Aborted by user.'; exit 0 }

# Build filter-repo args
$args = @()
foreach ($p in $PathsToRemove) { $args += '--path'; $args += $p }
$args += '--invert-paths'

Write-Host 'Running git-filter-repo...'
git filter-repo @args

Write-Host 'Filter complete. You must force-push cleaned branches to remote:'
Write-Host "git push --force --all"
Write-Host "git push --force --tags"
Write-Host 'Also revoke and rotate any exposed keys immediately (OpenAI, LangSmith, DB password).'
