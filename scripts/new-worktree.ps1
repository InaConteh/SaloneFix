<#
.SYNOPSIS
  Create an isolated git worktree for a feature branch, ready to run.

.DESCRIPTION
  - Creates ../salone-fix.wt/<slug> on branch <Name> (new branch off main, or existing).
  - Links the shared backend\.venv and frontend\node_modules via directory junctions
    (no reinstall, no duplicated gigabytes). Pass -FreshDeps to install separately instead.
  - Gives the worktree its own SQLite database, media folder and ports, so it can run
    side by side with the main checkout without touching its data.
  - Writes .claude\launch.json so the Claude desktop app can start both servers.

.EXAMPLE
  .\scripts\new-worktree.ps1 -Name feat/admin-ui
  .\scripts\new-worktree.ps1 -Name fix/media-auth -BackendPort 8002 -FrontendPort 5175
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $Name,
  [string] $Base = "main",
  [int] $BackendPort = 8001,
  [int] $FrontendPort = 5174,
  [switch] $FreshDeps
)

$ErrorActionPreference = "Stop"
# Git writes progress to stderr; PowerShell 5.1 would otherwise render it as an error.
$env:GIT_REDIRECT_STDERR = "2>&1"

$repo = (git rev-parse --show-toplevel).Trim()
if (-not $repo) { throw "Run this from inside the repository." }
$repo = $repo -replace "/", "\"

$slug = ($Name -replace "[^A-Za-z0-9._-]", "-").Trim("-")
$wtRoot = Join-Path (Split-Path $repo -Parent) "salone-fix.wt"
$target = Join-Path $wtRoot $slug

if (Test-Path $target) { throw "Worktree folder already exists: $target" }
New-Item -ItemType Directory -Force $wtRoot | Out-Null

# --- 1. worktree ------------------------------------------------------------
$branchExists = (git -C $repo branch --list $Name) -ne $null -and (git -C $repo branch --list $Name).Trim() -ne ""
if ($branchExists) {
  Write-Host "-> Adding worktree for existing branch '$Name'" -ForegroundColor Cyan
  git -C $repo worktree add $target $Name
} else {
  Write-Host "-> Creating branch '$Name' from '$Base' and adding worktree" -ForegroundColor Cyan
  git -C $repo worktree add -b $Name $target $Base
}
if ($LASTEXITCODE -ne 0) { throw "git worktree add failed." }

# --- 2. dependencies --------------------------------------------------------
function Link-Or-Install($linkPath, $sourcePath, $installScript, $label) {
  if ($FreshDeps -or -not (Test-Path $sourcePath)) {
    Write-Host "-> Installing $label (fresh)" -ForegroundColor Cyan
    & $installScript
  } else {
    Write-Host "-> Linking $label -> $sourcePath" -ForegroundColor Cyan
    New-Item -ItemType Junction -Path $linkPath -Target $sourcePath | Out-Null
  }
}

Link-Or-Install (Join-Path $target "backend\.venv") (Join-Path $repo "backend\.venv") {
  Push-Location (Join-Path $target "backend")
  python -m venv .venv
  & .\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
  Pop-Location
} "backend\.venv"

Link-Or-Install (Join-Path $target "frontend\node_modules") (Join-Path $repo "frontend\node_modules") {
  Push-Location (Join-Path $target "frontend")
  npm install --no-audit --no-fund
  Pop-Location
} "frontend\node_modules"

# --- 3. environment: own DB, own media, own ports ---------------------------
$backendEnvSrc = Join-Path $repo "backend\.env"
$backendEnv = Join-Path $target "backend\.env"
if (Test-Path $backendEnvSrc) {
  Copy-Item $backendEnvSrc $backendEnv
} else {
  Copy-Item (Join-Path $repo ".env.example") $backendEnv
}
# Make sure this worktree never points at the main checkout's data.
$envText = Get-Content $backendEnv -Raw
$envText = $envText -replace "(?m)^DATABASE_URL=.*$", "DATABASE_URL=sqlite:///./salonefix.db"
$envText = $envText -replace "(?m)^STORAGE_DIR=.*$", "STORAGE_DIR=./media_storage"
$envText = $envText -replace "(?m)^CORS_ORIGINS=.*$", "CORS_ORIGINS=http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort,http://localhost:5173"
Set-Content -Path $backendEnv -Value $envText -Encoding utf8

@"
VITE_API_BASE_URL=http://localhost:$BackendPort/api/v1
VITE_DEMO_PERSONAS=true
"@ | Set-Content -Path (Join-Path $target "frontend\.env.local") -Encoding utf8

# --- 4. launch config for the Claude desktop app ---------------------------
New-Item -ItemType Directory -Force (Join-Path $target ".claude") | Out-Null
@"
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "backend",
      "cwd": "backend",
      "runtimeExecutable": ".venv/Scripts/python.exe",
      "runtimeArgs": ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "$BackendPort"],
      "port": $BackendPort
    },
    {
      "name": "frontend",
      "cwd": "frontend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev", "--", "--port", "$FrontendPort", "--strictPort"],
      "port": $FrontendPort
    }
  ]
}
"@ | Set-Content -Path (Join-Path $target ".claude\launch.json") -Encoding utf8
# launch.json is tracked; keep this worktree's port-specific copy out of git status/commits.
git -C $target update-index --skip-worktree .claude/launch.json

# --- 5. summary -------------------------------------------------------------
Write-Host ""
Write-Host "Worktree ready:" -ForegroundColor Green
Write-Host "  path      $target"
Write-Host "  branch    $Name"
Write-Host "  backend   http://localhost:$BackendPort   (own salonefix.db + media_storage)"
Write-Host "  frontend  http://localhost:$FrontendPort"
Write-Host ""
Write-Host "Next:"
Write-Host "  cd `"$target`""
Write-Host "  .\scripts\check.ps1                      # run every gate on this branch"
Write-Host "  backend\.venv\Scripts\python.exe -m uvicorn main:app --port $BackendPort   (from backend\)"
Write-Host "  npm run dev -- --port $FrontendPort      (from frontend\)"
Write-Host ""
Write-Host "Remove later with:  .\scripts\remove-worktree.ps1 -Name $Name" -ForegroundColor DarkGray
