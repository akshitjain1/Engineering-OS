# Stop only processes this launcher started. Never kills arbitrary Python/Node.
param([switch] $Quiet)

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

if (-not (Test-Path $StateFile)) {
    Write-Log "No launcher-owned processes. Other Python/Node apps were left running."
    if (-not $Quiet) {
        Write-Host "If you started FastAPI or Next.js yourself, close those windows manually."
    }
    exit 0
}

$state = Get-Content -Raw -Path $StateFile | ConvertFrom-Json
Stop-OwnedPid -ProcessId $state.backendPid -Label "Backend"
Stop-OwnedPid -ProcessId $state.frontendPid -Label "Frontend"
Remove-Item -Force $StateFile -ErrorAction SilentlyContinue
Write-Log "Stop complete. Processes not started by the launcher were not touched."
exit 0
