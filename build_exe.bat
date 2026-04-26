@echo off
setlocal
cd /d "%~dp0"

py -3 -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
  py -3 -m pip install pyinstaller
)

py -3 -m PyInstaller ^
  --noconfirm ^
  --name NTEHDRPanel ^
  --noconsole ^
  --add-data "web;web" ^
  app.py

echo.
echo Build complete: dist\NTEHDRPanel\NTEHDRPanel.exe
pause
