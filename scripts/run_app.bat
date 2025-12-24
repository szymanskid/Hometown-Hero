@echo off
REM Run script for Hometown Hero Banner Management System with external data configuration
REM Edit the variables below to match your setup

echo ============================================
echo Hometown Hero Banner Management
echo Run Script
echo ============================================
echo.

REM ========================================
REM CONFIGURATION - Edit these paths
REM ========================================

REM Path to your Python virtual environment (venv)
REM Example: C:\Users\YourName\Hometown-Hero\venv
REM If empty, will use system Python
SET VENV_PATH=

REM Path to external data folder (where DB and config are stored)
REM Example: Q:\HHBanners2026-data
REM If empty, will use repo folder
SET DATA_DIR=

REM ========================================
REM End of configuration
REM ========================================

REM Activate virtual environment if specified
if not "%VENV_PATH%"=="" (
    echo Activating Python virtual environment: %VENV_PATH%
    if exist "%VENV_PATH%\Scripts\activate.bat" (
        call "%VENV_PATH%\Scripts\activate.bat"
    ) else (
        echo ERROR: Virtual environment not found at %VENV_PATH%
        echo Please update VENV_PATH in this script or leave it empty to use system Python
        pause
        exit /b 1
    )
    echo.
)

REM Set data paths if external data directory is specified
if not "%DATA_DIR%"=="" (
    echo Using external data directory: %DATA_DIR%
    
    REM Create data directory if it doesn't exist
    if not exist "%DATA_DIR%" (
        echo Creating data directory: %DATA_DIR%
        mkdir "%DATA_DIR%"
    )
    
    REM Set environment variables for data paths
    SET HH_DB_PATH=%DATA_DIR%\hometown_hero.db
    SET HH_M365_CONFIG=%DATA_DIR%\m365_config.json
    SET HH_EXPORT_DIR=%DATA_DIR%\exports
    
    echo   Database: %HH_DB_PATH%
    echo   M365 Config: %HH_M365_CONFIG%
    echo   Exports: %HH_EXPORT_DIR%
    echo.
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit is not installed
    echo Install dependencies with: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting Hometown Hero Banner Management GUI...
echo.
echo The application will open in your default browser.
echo To stop the application, press Ctrl+C in this window.
echo.

REM Run Streamlit
streamlit run gui_app.py
