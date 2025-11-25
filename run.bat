@echo off
REM Launch script for Windows
REM Telemetry Analysis Tool

echo ==========================================
echo Telemetry Analysis Tool - Launcher
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run the installation script first:
    echo   install-windows.bat
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.
echo Launching Telemetry Analysis Tool...
echo.

REM Launch the application
python src\main.py

REM Deactivate when done
call deactivate
