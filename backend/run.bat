@echo off
cd /d "%~dp0"
REM --reload so backend edits take effect without hunting down and restarting this
REM window. The launcher deliberately does not use it.
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
