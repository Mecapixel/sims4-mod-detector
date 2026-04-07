@echo off
title Sims 4 Bookshelf Culprit Finder
echo.
echo  Starting Bookshelf Browse Picker Culprit Finder...
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

:: Run the script from wherever this batch file is located
python "%~dp0find_bookshelf_culprit.py"
