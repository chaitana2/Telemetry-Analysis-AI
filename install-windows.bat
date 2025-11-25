@echo off
REM Automated installation script for Windows
REM Telemetry Analysis Tool

echo ==========================================
echo Telemetry Analysis Tool - Installer
echo For Windows 10/11
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
echo Checking Python version...
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo [OK] pip found

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded

REM Install dependencies
echo.
echo Installing Python dependencies...
echo This may take 2-5 minutes...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

REM Run tests
echo.
echo Running tests to verify installation...
pytest tests/ --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Some tests failed. Please check the output above.
) else (
    echo [OK] All tests passed!
)

REM Success message
echo.
echo ==========================================
echo Installation completed successfully!
echo ==========================================
echo.
echo To use the application:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo.
echo   2. Run the application:
echo      python src\main.py
echo.
echo   3. To deactivate the virtual environment:
echo      deactivate
echo.
echo For more information, see README.md
echo.
pause
