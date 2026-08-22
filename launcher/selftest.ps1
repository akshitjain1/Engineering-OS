# Launcher self-checks. Does not seed, migrate, or reset the database.
$ErrorActionPreference = "Stop"
$LauncherDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $LauncherDir "..")).Path
$Launch = Join-Path $LauncherDir "launch.ps1"
$Stop = Join-Path $LauncherDir "stop.ps1"
$Db = Join-Path $Root "backend\dev.db"
$failed = 0

function Assert-True($cond, $name) {
    if ($cond) {
        Write-Host "PASS  $name"
    } else {
        Write-Host "FAIL  $name"
        $script:failed++
    }
}

function Get-DbFingerprint($path) {
    if (-not (Test-Path $path)) { return $null }
    $item = Get-Item $path
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        $hash = [System.BitConverter]::ToString($sha.ComputeHash($stream)).Replace("-", "")
    } finally {
        $stream.Close()
        $sha.Dispose()
    }
    return @{ Hash = $hash; Length = $item.Length }
}

function Invoke-Launch {
    param([string[]] $Extra = @())
    $argList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Launch, "-NoBrowser", "-Quiet")
    foreach ($item in @($Extra)) {
        if ($null -ne $item -and $item -ne "") { $argList += $item }
    }
    & powershell.exe @argList
    return $LASTEXITCODE
}

Write-Host "Engineering OS launcher self-test"
Write-Host "---------------------------------"

$hashBefore = $null
$lenBefore = $null
$fpBefore = Get-DbFingerprint $Db
if ($fpBefore) {
    $hashBefore = $fpBefore.Hash
    $lenBefore = $fpBefore.Length
}

$health = $false
$front = $false
try {
    $h = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing -TimeoutSec 3
    $health = (($h.Content | ConvertFrom-Json).status -eq "ok")
} catch { }
try {
    $f = Invoke-WebRequest -Uri "http://127.0.0.1:3000/" -UseBasicParsing -TimeoutSec 3
    $front = ($f.StatusCode -ge 200 -and $f.StatusCode -lt 400)
} catch { }

Write-Host "Current backend health: $health"
Write-Host "Current frontend HTTP:  $front"

# 2/3/4/7 already-running + double launch
if ($health -and $front) {
    $c1 = Invoke-Launch
    Assert-True ($c1 -eq 0) "both already running: launch exits 0"
    $c2 = Invoke-Launch
    Assert-True ($c2 -eq 0) "double-click while running: launch exits 0"
} elseif ($health) {
    $c1 = Invoke-Launch
    Assert-True ($c1 -eq 0) "backend already running: launch does not fail"
} else {
    Write-Host "SKIP  already-running cases (backend not up); will try fresh start"
    $c1 = Invoke-Launch
    Assert-True ($c1 -eq 0) "fresh launcher start"
    $c2 = Invoke-Launch
    Assert-True ($c2 -eq 0) "second click after start"
}

# 5 backend startup failure (missing python, unused port — never opens sqlite)
$c5 = Invoke-Launch @("-PythonExe", "C:\EngineeringOS-missing-python.exe", "-BackendPort", "18001")
Assert-True ($c5 -ne 0) "backend startup failure returns error"

# 6 frontend startup failure
$c6 = Invoke-Launch @("-NodeExe", "C:\EngineeringOS-missing-node.exe", "-FrontendPort", "13001")
Assert-True ($c6 -ne 0) "frontend startup failure returns error"

# 10 app still works (before stop)
try {
    $h3 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing -TimeoutSec 5
    Assert-True ((($h3.Content | ConvertFrom-Json).status -eq "ok")) "GET /api/health still ok"
} catch {
    Assert-True $false "GET /api/health still ok"
}
try {
    $f3 = Invoke-WebRequest -Uri "http://127.0.0.1:3000/" -UseBasicParsing -TimeoutSec 5
    Assert-True ($f3.StatusCode -ge 200 -and $f3.StatusCode -lt 400) "GET :3000 still ok"
} catch {
    Write-Host "SKIP  GET :3000 (frontend not running)"
}

# 8 stop only launcher-owned PIDs
$ownedBeforeStop = $null
$ownedPath = Join-Path $LauncherDir "state\owned.json"
if (Test-Path $ownedPath) {
    $ownedBeforeStop = Get-Content -Raw $ownedPath | ConvertFrom-Json
}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Stop -Quiet
Assert-True ($LASTEXITCODE -eq 0) "stop script exits 0"
Start-Sleep -Seconds 2
if ($health) {
    $still = $false
    try {
        $h2 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing -TimeoutSec 3
        $still = (($h2.Content | ConvertFrom-Json).status -eq "ok")
    } catch { }
    Assert-True ($still) "stop did not kill a backend the launcher did not own"
}
if ($ownedBeforeStop -and $ownedBeforeStop.frontendPid) {
    $frontAfter = $false
    try {
        $fx = Invoke-WebRequest -Uri "http://127.0.0.1:3000/" -UseBasicParsing -TimeoutSec 3
        $frontAfter = ($fx.StatusCode -ge 200)
    } catch { }
    Assert-True (-not $frontAfter) "stop ended launcher-owned frontend"
}

# 9 database unchanged
if ($hashBefore) {
    $fpAfter = Get-DbFingerprint $Db
    Assert-True ($fpAfter.Hash -eq $hashBefore) "dev.db hash unchanged"
    Assert-True ($fpAfter.Length -eq $lenBefore) "dev.db size unchanged"
} else {
    Write-Host "SKIP  database hash (dev.db missing)"
}

if ($failed -gt 0) {
    Write-Host ""
    Write-Host "$failed launcher check(s) failed."
    exit 1
}
Write-Host ""
Write-Host "Launcher self-test passed."
exit 0
