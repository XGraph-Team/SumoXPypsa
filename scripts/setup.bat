@echo off
REM Manhattan Power Grid - Windows Setup Script
REM Automated setup for Windows environments

echo ======================================================
echo Manhattan Power Grid - Windows Setup
echo ======================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found
python --version

REM Check Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo [INFO] Python version: %PYTHON_VERSION%

REM Run the setup script
echo [INFO] Running setup script...
python scripts\setup.py

if errorlevel 1 (
    echo [ERROR] Setup failed
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Setup completed!
echo.
echo To start the application:
echo 1. Run: venv\Scripts\activate
echo 2. Run: python main_complete_integration.py
echo 3. Open: http://localhost:5000
echo.

pause