@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found.
  echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
  echo Select "Add Python to PATH" during installation, then run this file again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating the local Python environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

call ".venv\Scripts\activate.bat"
echo Installing or checking required packages...
python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Starting API RP 754 PSE Screening...
echo Keep this window open. Press Ctrl+C here to stop the application.
streamlit run app.py
goto :eof

:error
echo.
echo Setup failed. Check the message above, then try again.
pause
exit /b 1
