@echo off
REM Safe code update script for Hometown Hero Banner Management System
REM This script safely updates the code from GitHub without touching local data/config

echo ============================================
echo Hometown Hero Banner Management
echo Code Update Script
echo ============================================
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo Checking current status...
git status
echo.

REM Check if we have any uncommitted changes
git diff --quiet
if errorlevel 1 (
    echo WARNING: You have uncommitted changes in the repository
    echo This script will only update code files, not your data or config
    echo.
    echo Uncommitted changes:
    git status --short
    echo.
    set /p continue="Do you want to continue? (y/N): "
    if /i not "%continue%"=="y" (
        echo Update cancelled.
        pause
        exit /b 1
    )
)

echo.
echo Fetching latest code from GitHub...
git fetch origin main
if errorlevel 1 (
    echo ERROR: Failed to fetch from GitHub
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Checking if update is available...
git rev-list HEAD..origin/main --count > temp_count.txt
set /p UPDATE_COUNT=<temp_count.txt
del temp_count.txt

if "%UPDATE_COUNT%"=="0" (
    echo.
    echo Your code is already up to date!
    echo No updates needed.
    pause
    exit /b 0
)

echo.
echo Found %UPDATE_COUNT% new commit(s) available
echo.

REM Show what will be updated
echo Changes to be applied:
git log HEAD..origin/main --oneline
echo.

set /p confirm="Apply these updates? (y/N): "
if /i not "%confirm%"=="y" (
    echo Update cancelled.
    pause
    exit /b 1
)

echo.
echo Switching to main branch (if not already there)...
git switch main
if errorlevel 1 (
    echo ERROR: Failed to switch to main branch
    pause
    exit /b 1
)

echo.
echo Pulling updates (fast-forward only)...
git pull --ff-only origin main
if errorlevel 1 (
    echo.
    echo ERROR: Failed to update code
    echo This usually happens if you have local commits or conflicts
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure you haven't modified any code files directly
    echo 2. Your data files (hometown_hero.db, m365_config.json) are safe and won't be affected
    echo 3. If you need help, contact support
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS: Code updated successfully!
echo ============================================
echo.
echo Your data and configuration files were not affected:
echo - hometown_hero.db (database)
echo - m365_config.json (email config)
echo - .env (configuration)
echo.
echo If new dependencies were added, remember to update your environment:
echo   pip install -r requirements.txt
echo.
pause
