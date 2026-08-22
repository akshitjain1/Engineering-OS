# Engineering OS local launcher. Does not seed, migrate, or reset user data.
param(
    [int] $BackendPort = 8000,
    [int] $FrontendPort = 3000,
    [string] $PythonExe = "",
    [string] $NodeExe = "",
    [switch] $NoBrowser,
    [switch] $Quiet
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$LauncherDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $LauncherDir "..")).Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "ai-engine"
$LogDir = Join-Path $LauncherDir "logs"
$StateDir = Join-Path $LauncherDir "state"
$StateFile = Join-Path $StateDir "owned.json"
$LogFile = Join-Path $LogDir ("launcher-{0:yyyyMMdd}.log" -f (Get-Date))
$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$HealthUrl = "$BackendUrl/api/health"
$AppUrl = "$FrontendUrl/"

New-Item -ItemType Directory -Force -Path $LogDir, $StateDir | Out-Null

function Write-Log {
    param([string] $Message)
    $line = "{0:u} {1}" -f (Get-Date), $Message
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Show-Banner {
    if ($Quiet) { return }
    Write-Host ""
    Write-Host "Engineering OS"
    Write-Host "--------------"
    Write-Host "Starting your learning environment..."
    Write-Host ""
}

function Fail-Start {
    param(
        [string] $Service,
        [string] $Checked,
        [string] $Cause,
        [string] $Manual
    )
    $text = @"
ENGINEERING OS COULD NOT START

Service: $Service
Checked: $Checked
Likely cause: $Cause

Run this manually:
$Manual

Launcher log:
$LogFile
"@
    Write-Log "FAIL $Service :: $Cause"
    if (-not $Quiet) {
        Write-Host ""
        Write-Host $text
        try {
            Add-Type -AssemblyName System.Windows.Forms | Out-Null
            [System.Windows.Forms.MessageBox]::Show($text, "Engineering OS", "OK", "Error") | Out-Null
        } catch {
            Write-Host "Press Enter to close."
            [void][Console]::ReadLine()
        }
    }
    exit 1
}

function Read-OwnedState {
    if (-not (Test-Path $StateFile)) {
        return @{ backendPid = $null; frontendPid = $null }
    }
    try {
        return (Get-Content -Raw -Path $StateFile | ConvertFrom-Json)
    } catch {
        return @{ backendPid = $null; frontendPid = $null }
    }
}

function Write-OwnedState {
    param($State)
    $json = @{
        backendPid  = $State.backendPid
        frontendPid = $State.frontendPid
        backendPort = $BackendPort
        frontendPort = $FrontendPort
        updatedAt   = (Get-Date).ToString("o")
    } | ConvertTo-Json
    Set-Content -Path $StateFile -Value $json -Encoding UTF8
}

function Test-PortListening {
    param([int] $Port)
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(400)
        if ($ok) {
            try { $client.EndConnect($iar) } catch { $ok = $false }
        }
        $client.Close()
        return [bool] $ok
    } catch {
        return $false
    }
}

function Get-Http {
    param([string] $Url, [int] $TimeoutSec = 3)
    try {
        return Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -MaximumRedirection 5
    } catch {
        return $null
    }
}

function Test-BackendHealth {
    $resp = Get-Http -Url $HealthUrl
    if (-not $resp) { return $false }
    if ($resp.StatusCode -lt 200 -or $resp.StatusCode -ge 400) { return $false }
    try {
        $json = $resp.Content | ConvertFrom-Json
        return ($json.status -eq "ok")
    } catch {
        return $false
    }
}

function Test-FrontendHealth {
    $resp = Get-Http -Url $AppUrl
    if (-not $resp) { return $false }
    return ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400)
}

function Wait-Until {
    param(
        [scriptblock] $Probe,
        [int] $TimeoutSec,
        [string] $Label
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if (& $Probe) { return $true }
        Start-Sleep -Milliseconds 400
    }
    Write-Log "Timeout waiting for $Label after ${TimeoutSec}s"
    return $false
}

function Find-Command {
    param([string] $Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Start-LoggedCmd {
    param(
        [string] $FilePath,
        [string] $Arguments,
        [string] $WorkingDirectory,
        [string] $LogName
    )
    $logPath = Join-Path $LogDir $LogName
    $runner = Join-Path $StateDir ("run-" + $LogName + ".cmd")
    $lines = @(
        "@echo off",
        "cd /d `"$WorkingDirectory`"",
        "`"$FilePath`" $Arguments >> `"$logPath`" 2>&1"
    )
    Set-Content -Path $runner -Value $lines -Encoding ASCII
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$runner`"" -WorkingDirectory $WorkingDirectory -WindowStyle Minimized -PassThru
    Write-Log "Started PID $($proc.Id) ($LogName)"
    return $proc.Id
}

function Get-ManualBackend {
    return @"
cd /d `"$BackendDir`"
venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort
"@
}

function Get-ManualFrontend {
    return @"
cd /d `"$FrontendDir`"
npm run dev
"@
}

# --- mutex so a second click waits instead of spawning duplicates ---
$mutex = New-Object System.Threading.Mutex($false, "Global\EngineeringOS.LocalLauncher")
$ownedMutex = $false
try {
    $ownedMutex = $mutex.WaitOne(120000)
    if (-not $ownedMutex) {
        Fail-Start -Service "Launcher" -Checked "startup mutex (120s)" -Cause "Another launcher is still starting." -Manual (Get-ManualBackend)
    }

    Show-Banner

    $python = $PythonExe
    if (-not $python) {
        $python = Join-Path $BackendDir "venv\Scripts\python.exe"
    }
    $node = $NodeExe
    if (-not $node) {
        $node = Find-Command "node.exe"
        if (-not $node) { $node = Find-Command "node" }
    }
    $nextJs = Join-Path $FrontendDir "node_modules\next\dist\bin\next"
    $dbPath = Join-Path $BackendDir "dev.db"
    $mainPy = Join-Path $BackendDir "app\main.py"
    $pkg = Join-Path $FrontendDir "package.json"

    if (-not (Test-Path $mainPy)) {
        Fail-Start -Service "Launcher" -Checked $mainPy -Cause "Backend files were not found. The shortcut may not point at this repository." -Manual (Get-ManualBackend)
    }
    if (-not (Test-Path $pkg)) {
        Fail-Start -Service "Frontend" -Checked $pkg -Cause "The Next.js app folder was not found." -Manual (Get-ManualFrontend)
    }

    if (Test-Path $dbPath) {
        Write-Log "[OK] Database  (existing local SQLite; not modified by launcher)"
    } else {
        Write-Log "[!!] Database  (dev.db not found; launcher will not create or seed it)"
    }

    $state = Read-OwnedState
    $startedBackend = $false
    $startedFrontend = $false

    if (Test-BackendHealth) {
        Write-Log "[OK] Backend   already running on $BackendUrl"
    } elseif (Test-PortListening -Port $BackendPort) {
        Fail-Start -Service "Backend" -Checked $HealthUrl -Cause "Port $BackendPort is in use but /api/health did not return status=ok. Another program may own that port." -Manual (Get-ManualBackend)
    } else {
        if (-not (Test-Path $python)) {
            Fail-Start -Service "Backend" -Checked $python -Cause "The Python virtual environment is missing." -Manual @"
cd /d `"$BackendDir`"
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
$(Get-ManualBackend)
"@
        }
        Write-Log "Starting backend..."
        $state.backendPid = Start-LoggedCmd -FilePath $python -Arguments "-m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort" -WorkingDirectory $BackendDir -LogName "backend.log"
        $startedBackend = $true
        Write-OwnedState -State $state
        if (-not (Wait-Until -Probe { Test-BackendHealth } -TimeoutSec 45 -Label "backend /api/health")) {
            Fail-Start -Service "Backend" -Checked $HealthUrl -Cause "Python started but /api/health never succeeded. See launcher/logs/backend.log." -Manual (Get-ManualBackend)
        }
        Write-Log "[OK] Backend"
    }

    if (Test-FrontendHealth) {
        Write-Log "[OK] Frontend  already running on $FrontendUrl"
    } elseif (Test-PortListening -Port $FrontendPort) {
        Fail-Start -Service "Frontend" -Checked $AppUrl -Cause "Port $FrontendPort is in use but did not return a successful HTTP response." -Manual (Get-ManualFrontend)
    } else {
        if (-not $node -or -not (Test-Path $node)) {
            Fail-Start -Service "Frontend" -Checked "node on PATH" -Cause "Node.js is not installed or not on PATH." -Manual "Install Node.js LTS, then:`n$(Get-ManualFrontend)"
        }
        if (-not (Test-Path $nextJs)) {
            Fail-Start -Service "Frontend" -Checked $nextJs -Cause "Frontend dependencies are not installed." -Manual @"
cd /d `"$FrontendDir`"
npm install
npm run dev
"@
        }
        Write-Log "Starting frontend..."
        $state.frontendPid = Start-LoggedCmd -FilePath $node -Arguments "`"$nextJs`" dev --hostname 127.0.0.1 --port $FrontendPort" -WorkingDirectory $FrontendDir -LogName "frontend.log"
        $startedFrontend = $true
        Write-OwnedState -State $state
        if (-not (Wait-Until -Probe { Test-FrontendHealth } -TimeoutSec 90 -Label "frontend :$FrontendPort")) {
            Fail-Start -Service "Frontend" -Checked $AppUrl -Cause "Node started but http://127.0.0.1:$FrontendPort never became ready. See launcher/logs/frontend.log." -Manual (Get-ManualFrontend)
        }
        Write-Log "[OK] Frontend"
    }

    if (-not $startedBackend -and -not $startedFrontend) {
        Write-Log "Engineering OS is already running."
    }

    if (-not $NoBrowser) {
        Write-Log "Opening Engineering OS..."
        Start-Process $AppUrl | Out-Null
    } else {
        Write-Log "Browser open skipped (-NoBrowser)."
    }

    if (-not $Quiet) {
        Start-Sleep -Seconds 1
    }
    exit 0
}
finally {
    if ($ownedMutex) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
