# Push your learning history off this machine.
#
# dev.db is gitignored, so a normal `git push` backs up the code and none of the
# progress. This exports the database to JSON under backend/data/snapshot/ and
# commits and pushes only that path -- so it is safe to run mid-edit: nothing
# else you are working on is staged, committed, or touched.
param([switch] $Quiet)

$ErrorActionPreference = "Stop"
$LauncherDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $LauncherDir "..")).Path
$BackendDir = Join-Path $Root "backend"
$Python = Join-Path $BackendDir "venv\Scripts\python.exe"
$SnapshotPath = "backend/data/snapshot"

function Say { param([string] $Message) if (-not $Quiet) { Write-Host $Message } }

function Die {
    param([string] $Message)
    Write-Host ""
    Write-Host "BACKUP DID NOT COMPLETE"
    Write-Host $Message
    Write-Host ""
    Write-Host "Your data is not lost -- backend\backups\ still holds local snapshots."
    if (-not $Quiet) { Write-Host "Press Enter to close."; [void][Console]::ReadLine() }
    exit 1
}

Say ""
Say "Backing up Engineering OS to GitHub"
Say "-----------------------------------"

if (-not (Test-Path $Python)) { Die "Python virtual environment not found at:`n  $Python" }

Say "Exporting the database..."
$export = & $Python (Join-Path $BackendDir "scripts\export_db.py")
if ($LASTEXITCODE -ne 0) { Die "The export failed:`n  $($export -join "`n  ")" }
Say "  $(@($export)[0])"

# A local binary snapshot too, since we are here and it costs nothing.
& $Python (Join-Path $BackendDir "scripts\backup_db.py") | Out-Null

Push-Location $Root
try {
    $pending = & git status --porcelain -- $SnapshotPath
    if ($LASTEXITCODE -ne 0) { Die "This folder is not a git repository, or git is not on PATH." }

    if (-not $pending) {
        Say ""
        Say "Nothing new to back up -- the snapshot on GitHub already matches your database."
    } else {
        Say "Committing the snapshot..."
        & git add -- $SnapshotPath
        if ($LASTEXITCODE -ne 0) { Die "git add failed." }

        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        # Only this path is committed, so anything else in progress stays untouched.
        & git commit --only -- $SnapshotPath -m "Snapshot learning data ($stamp)" | Out-Null
        if ($LASTEXITCODE -ne 0) { Die "git commit failed." }
        Say "  committed"
    }

    $branch = (& git rev-parse --abbrev-ref HEAD).Trim()
    Say "Pushing $branch to GitHub..."
    $push = & git push origin $branch 2>&1
    if ($LASTEXITCODE -ne 0) {
        Die @"
The commit was made locally but the push failed:
  $($push -join "`n  ")

Your snapshot is committed -- run this again once the connection or
credentials are sorted, or push manually:
  git push origin $branch
"@
    }
    Say ""
    Say "Done. Your learning history is now on GitHub as well as this machine."
} finally {
    Pop-Location
}

if (-not $Quiet) { Start-Sleep -Seconds 2 }
exit 0
