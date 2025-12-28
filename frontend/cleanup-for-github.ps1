# ========================================
# GitHub Cleanup Script
# ========================================
# This script removes build artifacts that should not be committed to git
# Run this before your first git push

Write-Host "🧹 Cleaning up build artifacts for GitHub..." -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location $PSScriptRoot

# Remove build artifacts from git tracking
Write-Host "`n📦 Removing build folders from git..." -ForegroundColor Yellow
$foldersToRemove = @(
    "dist",
    "build",
    "coverage",
    "src/dist",
    "src/components/Order/dist",
    "src/services/dist"
)

foreach ($folder in $foldersToRemove) {
    if (Test-Path $folder) {
        Write-Host "  - Removing $folder from git tracking..." -ForegroundColor Gray
        git rm -r --cached $folder 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✓ Removed $folder" -ForegroundColor Green
        }
    }
}

# Remove node_modules if accidentally tracked
if (Test-Path "node_modules") {
    Write-Host "`n📦 Checking node_modules..." -ForegroundColor Yellow
    git rm -r --cached node_modules 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Removed node_modules from git" -ForegroundColor Green
    }
}

Write-Host "`n✅ Cleanup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Review changes: git status" -ForegroundColor White
Write-Host "2. Commit changes: git commit -m 'chore: remove build artifacts from git tracking'" -ForegroundColor White
Write-Host "3. Verify .gitignore is working: git status (should not show dist/build folders)" -ForegroundColor White
Write-Host "4. Push to GitHub: git push" -ForegroundColor White
