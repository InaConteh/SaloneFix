<#
.SYNOPSIS
  Remove a worktree created by new-worktree.ps1 without touching shared dependencies.

.DESCRIPTION
  The worktree's backend\.venv and frontend\node_modules are directory JUNCTIONS into the
  main checkout. A naive recursive delete (or `git worktree remove --force` on some Git
  builds) can follow them and wipe the real folders. This script unlinks the junctions
  first, then lets git remove the worktree, then optionally deletes the branch.

.EXAMPLE
  .\scripts\remove-worktree.ps1 -Name feat/admin-ui
  .\scripts\remove-worktree.ps1 -Name feat/admin-ui -DeleteBranch
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $Name,
  [switch] $DeleteBranch,
  [switch] $Force
)

$ErrorActionPreference = "Stop"
# Git writes progress to stderr; PowerShell 5.1 would otherwise render it as an error.
$env:GIT_REDIRECT_STDERR = "2>&1"

$repo = (git rev-parse --show-toplevel).Trim() -replace "/", "\"
$slug = ($Name -replace "[^A-Za-z0-9._-]", "-").Trim("-")
$target = Join-Path (Join-Path (Split-Path $repo -Parent) "salone-fix.wt") $slug

if (-not (Test-Path $target)) { throw "No worktree folder at $target" }
if ((Resolve-Path $target).Path -eq $repo) { throw "Refusing to remove the main checkout." }

# Refuse to drop uncommitted work unless told to.
$dirty = git -C $target status --porcelain
if ($dirty -and -not $Force) {
  Write-Host $dirty
  throw "Worktree has uncommitted changes. Commit/stash them, or re-run with -Force to discard."
}

# 1. Unlink junctions (removes the link only, never the target contents).
foreach ($rel in @("backend\.venv", "frontend\node_modules")) {
  $p = Join-Path $target $rel
  if (Test-Path $p) {
    $item = Get-Item $p -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      Write-Host "-> Unlinking junction $rel" -ForegroundColor Cyan
      [IO.Directory]::Delete($p)
    } else {
      Write-Host "-> $rel is a real folder (fresh install); it will be deleted with the worktree" -ForegroundColor DarkGray
    }
  }
}

# 2. Remove the worktree.
Write-Host "-> git worktree remove" -ForegroundColor Cyan
if ($Force) { git -C $repo worktree remove --force $target } else { git -C $repo worktree remove $target }
if ($LASTEXITCODE -ne 0) { throw "git worktree remove failed." }
git -C $repo worktree prune

# 3. Optionally delete the branch (only if merged, unless -Force).
if ($DeleteBranch) {
  Write-Host "-> Deleting branch $Name" -ForegroundColor Cyan
  if ($Force) { git -C $repo branch -D $Name } else { git -C $repo branch -d $Name }
}

Write-Host "Done." -ForegroundColor Green
