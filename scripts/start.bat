@echo off
REM ReSan Bank - Quick Start Script for Windows
REM This script sets up and runs the application

REM Change to project root directory (parent of scripts folder)
cd /d "%~dp0\.."

echo.
echo ========================================
echo    ReSan Bank - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if virtual environment exists
if not exist ".venv" (
    echo.
    echo Creating virtual environment...
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
echo [OK] Dependencies installed

REM Check for .env file
echo.
if exist "config\.env" (
    echo [OK] config\.env file found - SMS may be enabled
    copy config\.env .env >nul
) else if exist ".env" (
    echo [OK] .env file found - SMS may be enabled
) else (
    echo [INFO] No .env file - running in dev mode (OTP in console^)
    echo        To enable SMS: copy config\.env.example config\.env and add Twilio credentials
)

REM Check if data file exists
if not exist "resan_data.json" (
    echo.
    echo Creating initial data file...
    echo {"accounts":{},"transactions":{}}> resan_data.json
    echo [OK] Data file created
)

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    mkdir uploads
    echo [OK] Uploads directory created
)

echo.
echo ========================================
echo    Starting ReSan Bank...
echo ========================================
echo.
echo    App will be available at: http://localhost:8000
echo    API docs available at: http://localhost:8000/docs
echo.
echo    Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Run the application
python main.py

pause
