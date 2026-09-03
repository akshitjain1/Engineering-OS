# Stop only processes this launcher started. Never kills arbitrary Python/Node.
param(
    [switch] $Quiet,
    # Skip the GitHub push. Used when a script stops the app as part of some
    # other job and does not want a commit as a side effect.
    [switch] $NoSync
)

$ErrorActionPreference = "Stop"
$LauncherDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StateFile = Join-Path $LauncherDir "state\owned.json"
$LogDir = Join-Path $LauncherDir "logs"
$LogFile = Join-Path $LogDir ("launcher-{0:yyyyMMdd}.log" -f (Get-Date))
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string] $Message)
    Add-Content -Path $LogFile -Value ("{0:u} {1}" -f (Get-Date), $Message) -Encoding UTF8
    if (-not $Quiet) { Write-Host $Message }
}

function Get-CommandLine([int] $ProcessId) {
    try {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
        if ($p) { return [string] $p.CommandLine }
    } catch { }
    return ""
}

function Test-OwnedCommand([string] $CommandLine) {
    if (-not $CommandLine) { return $false }
    $c = $CommandLine.ToLowerInvariant()
    return (
        $c.Contains("uvicorn") -or
        $c.Contains("next") -or
        $c.Contains("run-backend") -or
        $c.Contains("run-frontend") -or
        $c.Contains("\launcher\state\run-")
    )
}

function Stop-OwnedPid {
    param([Nullable[int]] $ProcessId, [string] $Label)
    if (-not $ProcessId) {
        Write-Log "${Label}: no launcher-owned PID recorded."
        return
    }
    $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Log "${Label}: PID $ProcessId is not running."
        return
    }
    $cmd = Get-CommandLine -ProcessId $ProcessId
    $childMatch = $false
    try {
        $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
        foreach ($child in @($children)) {
            if (Test-OwnedCommand ([string] $child.CommandLine)) { $childMatch = $true }
        }
    } catch { }
    if (-not (Test-OwnedCommand $cmd) -and -not $childMatch) {
        Write-Log "${Label}: PID $ProcessId does not look like an Engineering OS process. Not killing it."
        Write-Log "  Command line: $cmd"
        return
    }
    Write-Log "${Label}: stopping PID $ProcessId (tree)"
    & taskkill.exe /PID $ProcessId /T /F | Out-Null
}

if (-not $Quiet) {
    Write-Host "Engineering OS Stop"
    Write-Host "-------------------"
}

function Sync-ToGitHub {
    <#
        Export the day's work and push it, on the way out.

        Runs after the servers are down, so nothing is mid-write and the export
        is a clean picture of the day you just finished. It commits only
        backend/data/snapshot, so anything else in the working tree is left
        alone.

        Best effort, always. Closing the app is not allowed to fail because the
        network is down, a push was rejected, or git is not on PATH -- the
        local snapshot in backend\backups\ has already been taken by then.
    #>
    $script = Join-Path $LauncherDir "backup-to-github.ps1"
    if (-not (Test-Path $script)) {
        Write-Log "Backup: backup-to-github.ps1 is missing, nothing pushed."
        return
    }
    Write-Log "Backing up today's work to GitHub..."
    try {
        $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -BestEffort
        foreach ($line in @($output)) {
            if ("$line".Trim()) { Write-Log "  $line" }
        }
    } catch {
        Write-Log "  GitHub backup failed: $($_.Exception.Message)"
        Write-Log "  Your data is safe - backend\backups\ still holds today's local snapshot."
    }
}

if (-not (Test-Path $StateFile)) {
    Write-Log "No launcher-owned processes. Other Python/Node apps were left running."
    if (-not $Quiet) {
        Write-Host "If you started FastAPI or Next.js yourself, close those windows manually."
    }
    # Still worth syncing: the app may have been stopped some other way, and
    # the day's work is sitting unpushed either way.
    if (-not $NoSync) { Sync-ToGitHub }
    exit 0
}

$state = Get-Content -Raw -Path $StateFile | ConvertFrom-Json
Stop-OwnedPid -ProcessId $state.backendPid -Label "Backend"
Stop-OwnedPid -ProcessId $state.frontendPid -Label "Frontend"
Remove-Item -Force $StateFile -ErrorAction SilentlyContinue
Write-Log "Stop complete. Processes not started by the launcher were not touched."

if (-not $NoSync) { Sync-ToGitHub }
exit 0
