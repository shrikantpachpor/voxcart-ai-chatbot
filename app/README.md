# VoxCart (app)

Important repository hygiene steps for publishing:

- Do NOT commit real secrets. Remove or rotate any exposed keys immediately.
- Store secrets in a local `.env` (listed in `.gitignore`) and use `.env.example` for the template.
- If secrets were already committed, purge history with `git filter-repo` or BFG and rotate keys.

Quick remediation commands (run from repo root):

```powershell
# 1) Remove sensitive file from working tree and add to .gitignore
git rm --cached app/.env
git commit -m "remove .env from repo"

# 2) Purge secrets from git history (example using git-filter-repo)
# Install: pip install git-filter-repo
git filter-repo --path app/.env --invert-paths

# 3) Rotate all exposed keys (OpenAI, LangSmith, DB passwords) immediately via provider consoles
```

Recommended next steps:
- Revoke and re-create the OpenAI and LangSmith API keys currently shown in `app/.env`.
- Change the database password and update your local `.env` accordingly.
- Run a secrets scan (gitleaks) on the repo before pushing.

## Scripts included

- `app/scripts/purge_secrets.ps1` - PowerShell helper which runs `git-filter-repo` to remove specific paths from history. Run from repo root.
- `app/scripts/purge_secrets.sh` - Bash equivalent.
- `app/scripts/run_gitleaks.ps1` - Run `gitleaks detect --source .` locally on Windows/PowerShell.

## Recommended usage

1. Revoke and rotate keys in provider consoles (OpenAI, LangSmith, DB).
2. Backup your repo: `git clone --mirror . ../repo-backup.git`
3. From repo root, run the purge script (PowerShell example):

```powershell
cd ..\voxcart
.\app\scripts\purge_secrets.ps1
```

4. Force-push cleaned history (after verifying):

```powershell
git push --force --all
git push --force --tags
```

5. Run `gitleaks` locally to confirm no secrets remain.

