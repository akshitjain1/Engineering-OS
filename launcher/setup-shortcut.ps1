# Creates Desktop shortcuts. Does not modify the learning app or database.
$ErrorActionPreference = "Stop"
$LauncherDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Desktop = [Environment]::GetFolderPath("Desktop")
$Wsh = New-Object -ComObject WScript.Shell

function New-EosShortcut {
    param([string] $Name, [string] $Vbs)
    $path = Join-Path $Desktop $Name
    $sc = $Wsh.CreateShortcut($path)
    $sc.TargetPath = Join-Path $env:SystemRoot "System32\wscript.exe"
    $sc.Arguments = "//nologo `"$Vbs`""
    $sc.WorkingDirectory = $LauncherDir
    $sc.WindowStyle = 1
    $sc.Description = "Engineering OS local learning workspace"
    $pythonIco = Join-Path $LauncherDir "..\backend\venv\Scripts\python.exe"
    if (Test-Path $pythonIco) {
        $sc.IconLocation = (Resolve-Path $pythonIco).Path
    }
    $sc.Save()
    return $path
}

$start = New-EosShortcut -Name "Engineering OS.lnk" -Vbs (Join-Path $LauncherDir "start.vbs")
$stop = New-EosShortcut -Name "Engineering OS Stop.lnk" -Vbs (Join-Path $LauncherDir "stop.vbs")

Write-Host "Created:"
Write-Host "  $start"
Write-Host "  $stop"
Write-Host ""
Write-Host "Double-click Engineering OS on your Desktop to study."
