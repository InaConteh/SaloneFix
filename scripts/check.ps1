<#
.SYNOPSIS
  Run every quality gate for the current checkout (main or any worktree) and print a scoreboard.

.DESCRIPTION
  Gates, in order:
    1. Backend: migrations apply to an empty database
    2. Backend: app imports with no AI/WhatsApp configuration (human-first rule)
    3. Backend: pytest
    4. Frontend: oxlint (must be warning-free)
    5. Frontend: vitest
    6. Frontend: production build
  Exit code is non-zero if any gate fails, so it can be used as a pre-push check.

.EXAMPLE
  .\scripts\check.ps1            # everything
  .\scripts\check.ps1 -Backend   # backend gates only
  .\scripts\check.ps1 -Frontend  # frontend gates only
  .\scripts\check.ps1 -Quick     # skip the production build
#>
[CmdletBinding()]
param(
  [switch] $Backend,
  [switch] $Frontend,
  [switch] $Quick
)

$ErrorActionPreference = "Continue"
# Git writes progress to stderr; PowerShell 5.1 would otherwise render it as an error.
$env:GIT_REDIRECT_STDERR = "2>&1"
$repo = (git rev-parse --show-toplevel).Trim() -replace "/", "\"
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
$runAll = -not ($Backend -or $Frontend)

$py = Join-Path $repo "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$results = New-Object System.Collections.ArrayList
$sw = [Diagnostics.Stopwatch]::StartNew()

function Gate($name, [scriptblock] $body) {
  Write-Host ""
  Write-Host ("=" * 70) -ForegroundColor DarkGray
  Write-Host " $name" -ForegroundColor Cyan
  Write-Host ("=" * 70) -ForegroundColor DarkGray
  $t = [Diagnostics.Stopwatch]::StartNew()
  $global:LASTEXITCODE = 0
  & $body
  $ok = ($LASTEXITCODE -eq 0)
  $t.Stop()
  [void] $results.Add([pscustomobject]@{ Gate = $name; Result = $(if ($ok) { "PASS" } else { "FAIL" }); Seconds = [math]::Round($t.Elapsed.TotalSeconds, 1) })
  if (-not $ok) { Write-Host " -> FAIL" -ForegroundColor Red } else { Write-Host " -> PASS" -ForegroundColor Green }
}

Write-Host "SaloneFix check  |  $repo  |  branch: $branch" -ForegroundColor Yellow

if ($runAll -or $Backend) {
  Push-Location (Join-Path $repo "backend")
  $tmpDb = Join-Path $env:TEMP ("salonefix-check-{0}.db" -f [guid]::NewGuid().ToString("N"))

  Gate "backend: alembic upgrade head on empty DB" {
    $env:DATABASE_URL = "sqlite:///$($tmpDb -replace '\\','/')"
    & $py -m alembic upgrade head 2>&1 | Select-String -NotMatch "^INFO" | Out-Host
  }
  Gate "backend: app starts with AI/WhatsApp absent" {
    $env:DATABASE_URL = "sqlite:///$($tmpDb -replace '\\','/')"
    $env:AI_API_KEY = ""; $env:WHATSAPP_TOKEN = ""
    & $py -c "import main; print('import ok')" 2>&1 | Select-String -NotMatch '^\{' | Out-Host
  }
  Remove-Item $tmpDb -ErrorAction SilentlyContinue
  Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue

  Gate "backend: pytest" {
    $env:APP_ENV = "test"
    & $py -m pytest -q -p no:cacheprovider 2>&1 | Select-Object -Last 3 | Out-Host
  }
  Pop-Location
}

if ($runAll -or $Frontend) {
  Push-Location (Join-Path $repo "frontend")
  Gate "frontend: oxlint (warning-free)" {
    $out = & npx --no-install oxlint --deny-warnings 2>&1
    $out | Select-String -NotMatch "npm notice" | Out-Host
  }
  Gate "frontend: vitest" {
    & npx --no-install vitest run --reporter=dot 2>&1 | Select-String -NotMatch "npm notice" | Select-Object -Last 6 | Out-Host
  }
  if (-not $Quick) {
    Gate "frontend: production build" {
      & npm run build 2>&1 | Select-String -NotMatch "npm notice" | Select-Object -Last 4 | Out-Host
    }
  }
  Pop-Location
}

$sw.Stop()
Write-Host ""
Write-Host ("-" * 70)
$results | Format-Table -AutoSize | Out-Host
$failed = @($results | Where-Object { $_.Result -eq "FAIL" }).Count
if ($failed -eq 0) {
  Write-Host ("ALL GATES PASSED  ({0}s)  -  branch '{1}' is safe to push / merge." -f [math]::Round($sw.Elapsed.TotalSeconds), $branch) -ForegroundColor Green
  exit 0
} else {
  Write-Host ("{0} GATE(S) FAILED  ({1}s)  -  do not merge '{2}'." -f $failed, [math]::Round($sw.Elapsed.TotalSeconds), $branch) -ForegroundColor Red
  exit 1
}
