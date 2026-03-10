@echo off
echo Starting local server for TNP Intelligence Hub...
echo.
echo URL: http://localhost:8000
echo Ctrl+C to stop.
echo.
cd /d "%~dp0"
python -m http.server 8000
pause
