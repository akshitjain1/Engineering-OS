@echo off
setlocal
cd /d "%~dp0"
echo Creating Desktop shortcuts for Engineering OS...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-shortcut.ps1"
if errorlevel 1 (
  echo Shortcut setup failed.
  pause
  exit /b 1
)
echo.
echo Done. You can close this window.
pause
